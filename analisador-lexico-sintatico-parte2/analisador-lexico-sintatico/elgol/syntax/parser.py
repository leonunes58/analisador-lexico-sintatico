import ply.yacc as yacc

from lexer.lexer import tokens  # noqa: F401  (o PLY lê a lista de tokens deste módulo)
from syntax.ast import Node

TOKEN_DESCRIPTIONS = {
    "ID": "identificador",
    "FUNCID": "nome de função",
    "NUMBER": "número",
    "ASSIGN": "'='",
    "PLUS": "'+'",
    "MINUS": "'-'",
    "DIV": "'/'",
    "MULT": "'x'",
    "DOT": "'.'",
    "LPAREN": "'('",
    "RPAREN": "')'",
    "COMMA": "','",
    "ELGIO": "'elgio'",
    "DECIMAL": "'DECIMAL'",
    "Z": "'_Z_'",
    "NEG": "'_NEG_'",
    "EXP": "'EXP'",
    "RESTO": "'RESTO'",
    "ENQUANTO": "'enquanto'",
    "SE": "'se'",
    "ENTAO": "'entao'",
    "SENAO": "'senao'",
    "PARA": "'para'",
    "INICIO": "'inicio'",
    "FIM": "'fim'",
    "MAIOR": "'maior'",
    "MENOR": "'menor'",
    "IGUAL": "'igual'",
    "DIFERENTE": "'diferente'",
    "MIGUAL": "'migual'",
    "MIGUAL_CAP": "'MIgual'",
    "$end": "fim do arquivo",
}

precedence = (
    ("left", "PLUS", "MINUS"),
    ("left", "MULT", "DIV", "RESTO"),
    ("right", "NEG"),
    ("right", "EXP"),
)

syntax_errors = []
start = "programa"


# ---------------------------------------------------------------- programa

def p_programa(p):
    "programa : INICIO comandos FIM"
    p[0] = Node("programa", p[2], lineno=p.lineno(1))


# ---------------------------------------------------------------- comandos

def p_comandos_lista(p):
    "comandos : comandos comando"
    p[0] = p[1] + [p[2]]


def p_comandos_vazio(p):
    "comandos : "
    p[0] = []


def p_comando(p):
    """comando : atribuicao
               | declaracao
               | condicional
               | repeticao_enquanto
               | repeticao_para
               | chamada_comando"""
    p[0] = p[1]


def p_comando_erro(p):
    "comando : error DOT"
    p[0] = Node("erro", lineno=p.lineno(2))


def p_atribuicao(p):
    "atribuicao : ID ASSIGN expressao DOT"
    p[0] = Node("atribuicao", [Node("id", value=p[1]), p[3]], lineno=p.lineno(1))


def p_declaracao(p):
    "declaracao : DECIMAL ID DOT"
    p[0] = Node("declaracao", [Node("id", value=p[2])], value="DECIMAL", lineno=p.lineno(1))


def p_condicional_simples(p):
    "condicional : SE LPAREN condicao RPAREN ENTAO comandos FIM"
    p[0] = Node("se", [p[3], Node("entao", p[6])], lineno=p.lineno(1))


def p_condicional_composto(p):
    "condicional : SE LPAREN condicao RPAREN ENTAO comandos SENAO comandos FIM"
    p[0] = Node("se", [p[3], Node("entao", p[6]), Node("senao", p[8])], lineno=p.lineno(1))


def p_repeticao_enquanto(p):
    "repeticao_enquanto : ENQUANTO LPAREN condicao RPAREN ENTAO comandos FIM"
    p[0] = Node("enquanto", [p[3], Node("corpo", p[6])], lineno=p.lineno(1))


def p_repeticao_para(p):
    "repeticao_para : PARA LPAREN condicao RPAREN ENTAO comandos FIM"
    p[0] = Node("para", [p[3], Node("corpo", p[6])], lineno=p.lineno(1))


def p_chamada_comando(p):
    "chamada_comando : chamada DOT"
    p[0] = p[1]


# ---------------------------------------------------------------- funções

def p_chamada(p):
    "chamada : FUNCID LPAREN argumentos RPAREN"
    p[0] = Node("chamada", p[3], value=p[1], lineno=p.lineno(1))


def p_argumentos(p):
    """argumentos : lista_argumentos
                  | """
    p[0] = p[1] if len(p) > 1 else []


def p_lista_argumentos_um(p):
    "lista_argumentos : expressao"
    p[0] = [p[1]]


def p_lista_argumentos_varios(p):
    "lista_argumentos : lista_argumentos COMMA expressao"
    p[0] = p[1] + [p[3]]


# ---------------------------------------------------------------- condição

def p_condicao(p):
    "condicao : expressao relacional expressao"
    p[0] = Node("condicao", [p[1], p[3]], value=p[2])


def p_relacional(p):
    """relacional : MAIOR
                  | MENOR
                  | IGUAL
                  | DIFERENTE
                  | MIGUAL
                  | MIGUAL_CAP"""
    p[0] = p[1]


# ---------------------------------------------------------------- expressões

def p_expressao_binaria(p):
    """expressao : expressao PLUS expressao
                 | expressao MINUS expressao
                 | expressao MULT expressao
                 | expressao DIV expressao
                 | expressao RESTO expressao
                 | expressao EXP expressao"""
    p[0] = Node("operacao", [p[1], p[3]], value=p[2])


def p_expressao_neg(p):
    "expressao : NEG expressao"
    p[0] = Node("negativo", [p[2]], value="_NEG_")


def p_expressao_parenteses(p):
    "expressao : LPAREN expressao RPAREN"
    p[0] = p[2]


def p_expressao_comparacao(p):
    "expressao : LPAREN condicao RPAREN"
    p[0] = p[2]


def p_expressao_id(p):
    "expressao : ID"
    p[0] = Node("id", value=p[1])


def p_expressao_numero(p):
    "expressao : NUMBER"
    p[0] = Node("numero", value=p[1])


def p_expressao_zero(p):
    "expressao : Z"
    p[0] = Node("zero", value="_Z_")


def p_expressao_chamada(p):
    "expressao : chamada"
    p[0] = p[1]


# ---------------------------------------------------------------- erros

def _expected_tokens():
    state = getattr(_parser, "state", None)
    if state is None:
        return []
    actions = _parser.action.get(state, {})
    names = [t for t in actions if t != "error"]
    return sorted(TOKEN_DESCRIPTIONS.get(t, t) for t in names)


def p_error(tok):
    expected = _expected_tokens()
    hint = ""
    if expected and len(expected) <= 6:
        hint = f"; esperado: {', '.join(expected)}"

    if tok is None:
        syntax_errors.append((None, f"fim de arquivo inesperado (faltou 'fim'?){hint}"))
        return

    found = TOKEN_DESCRIPTIONS.get(tok.type, tok.type)
    syntax_errors.append(
        (tok.lineno, f"token inesperado {found} = {tok.value!r}{hint}")
    )


def _build_parser():
    kwargs = dict(debug=False, errorlog=yacc.NullLogger())
    try:
        return yacc.yacc(write_tables=False, **kwargs)
    except TypeError:
        return yacc.yacc(**kwargs)


_parser = _build_parser()


class _TokenStream:

    def __init__(self, toks):
        self._it = iter(toks)

    def token(self):
        return next(self._it, None)

    def input(self, _data):
        pass


def parse(token_list):
    global syntax_errors
    syntax_errors = []
    tree = _parser.parse(lexer=_TokenStream(token_list))
    return tree, list(syntax_errors)
