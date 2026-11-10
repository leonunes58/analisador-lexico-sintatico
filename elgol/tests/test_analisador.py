from pathlib import Path

import pytest

from analyzer import analyze

EXEMPLOS = Path(__file__).parent / "exemplos"
CORRETOS = sorted((EXEMPLOS / "corretos").glob("*.elgol")) + [Path(__file__).parent / "correto.elgol"]
INCORRETOS = sorted((EXEMPLOS / "incorretos").glob("*.elgol"))

# arquivo -> linhas em que esperamos erro sintático (None = fim do arquivo)
ERROS_SINTATICOS_ESPERADOS = {
    "01_sem_ponto.elgol": [4],
    "02_sem_fim.elgol": [None],
    "03_sem_entao.elgol": [5],
    "04_operador_faltando.elgol": [3],
    "05_condicao_sem_relacional.elgol": [4],
    "06_atribuicao_invalida.elgol": [3],
    "07_parenteses.elgol": [3],
    "08_sem_inicio.elgol": [2],
    "09_senao_sem_se.elgol": [4],
    "10_varios_erros.elgol": [3, 5, 6],
    "11_lexico_e_sintatico.elgol": [3, 4],
}


def run(src):
    return analyze(src)


def linhas(errors):
    return [lineno for lineno, _ in errors]


# ---------------------------------------------------------------- arquivos de exemplo

@pytest.mark.parametrize("arquivo", CORRETOS, ids=lambda p: p.name)
def test_exemplos_corretos_sao_aceitos(arquivo):
    result = run(arquivo.read_text(encoding="utf-8"))
    assert result.lexical_errors == []
    assert result.syntax_errors == []
    assert result.tree is not None and result.tree.kind == "programa"


@pytest.mark.parametrize("arquivo", INCORRETOS, ids=lambda p: p.name)
def test_exemplos_incorretos_sao_rejeitados(arquivo):
    result = run(arquivo.read_text(encoding="utf-8"))
    assert not result.ok
    assert linhas(result.syntax_errors) == ERROS_SINTATICOS_ESPERADOS[arquivo.name]


def test_todos_os_incorretos_tem_expectativa():
    assert {p.name for p in INCORRETOS} == set(ERROS_SINTATICOS_ESPERADOS)


def test_exemplo_lexico_da_parte1_continua_detectando_erros():
    result = run((Path(__file__).parent / "incorreto.elgol").read_text(encoding="utf-8"))
    assert len(result.lexical_errors) == 9


# ---------------------------------------------------------------- estrutura da árvore

def programa(*comandos):
    return "inicio\n" + "\n".join(comandos) + "\nfim\n"


def expr_da_atribuicao(src_expr):
    result = run(programa(f"Valor = {src_expr}."))
    assert result.ok, result.syntax_errors
    return result.tree.children[0].children[1]


def test_multiplicacao_tem_precedencia_sobre_soma():
    e = expr_da_atribuicao("Base + Base x 2")
    assert e.value == "+"
    assert e.children[1].value == "x"


def test_operadores_de_mesma_precedencia_associam_a_esquerda():
    e = expr_da_atribuicao("Base - 2 - 1")
    assert e.value == "-"
    assert e.children[0].value == "-"
    assert e.children[1].value == 1


def test_exp_associa_a_direita():
    e = expr_da_atribuicao("2 EXP 3 EXP 2")
    assert e.value == "EXP"
    assert e.children[0].value == 2
    assert e.children[1].value == "EXP"


def test_exp_tem_precedencia_sobre_neg():
    e = expr_da_atribuicao("_NEG_ 2 EXP 2")
    assert e.kind == "negativo"
    assert e.children[0].value == "EXP"


def test_parenteses_alteram_precedencia():
    e = expr_da_atribuicao("(Base + 1) x 2")
    assert e.value == "x"
    assert e.children[0].value == "+"


def test_resto_tem_mesma_precedencia_que_multiplicacao():
    e = expr_da_atribuicao("Base + 7 RESTO 3")
    assert e.value == "+"
    assert e.children[1].value == "RESTO"


def test_senao_gera_ramo_proprio():
    result = run(programa("se (Base maior 1) entao", "Base = 1.", "senao", "Base = 2.", "fim"))
    assert result.ok
    se = result.tree.children[0]
    assert [c.kind for c in se.children] == ["condicao", "entao", "senao"]
    assert se.children[0].value == "maior"


@pytest.mark.parametrize("op", ["maior", "menor", "igual", "diferente", "migual", "MIgual"])
def test_todos_os_relacionais(op):
    result = run(programa(f"enquanto (Base {op} 3) entao", "fim"))
    assert result.ok, result.syntax_errors
    assert result.tree.children[0].children[0].value == op


def test_chamada_de_funcao_com_argumentos():
    result = run(programa("$Somar(Base, 2, $Dobro(Base))."))
    assert result.ok
    chamada = result.tree.children[0]
    assert chamada.kind == "chamada" and chamada.value == "$Somar"
    assert len(chamada.children) == 3


def test_chamada_sem_argumentos():
    assert run(programa("$Limpar().")).ok


# ---------------------------------------------------------------- erros pontuais

@pytest.mark.parametrize(
    "comando",
    [
        "Valor = .",                 # expressão vazia
        "Valor = 1 + .",             # operando faltando
        "Valor 1.",                  # falta '='
        "Valor = 1",                 # falta '.' (o 'fim' vira o token inesperado)
        "se Valor maior 1 entao fim",  # condição sem parênteses
        "para (Valor) entao fim",    # condição sem relacional
        "Valor = $Somar(1,).",       # argumento vazio
        "DECIMAL 10.",               # declaração sem identificador
        "fim",                       # 'fim' sobrando
    ],
)
def test_comandos_invalidos(comando):
    result = run(programa(comando))
    assert result.syntax_errors, f"deveria falhar: {comando!r}"


def test_programa_vazio_eh_invalido():
    result = run("")
    assert result.syntax_errors == [(None, result.syntax_errors[0][1])]


def test_recuperacao_continua_apos_erro():
    result = run(programa("Valor = 1 +.", "Base = 2.", "Novo = x.", "Pronto = 3."))
    assert linhas(result.syntax_errors) == [2, 4]


def test_analises_consecutivas_sao_independentes():
    assert not run(programa("Valor = .")).ok
    assert run(programa("Valor = 1.")).ok
