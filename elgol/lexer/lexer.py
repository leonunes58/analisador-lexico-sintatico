import re

import ply.lex as lex

from symbols.symbols_table import SymbolTable

# Palavras reservadas da linguagem Elgol -> nome do token PLY.
# 'migual' e 'MIgual' são tokens distintos pois a linguagem é
# case-sensitive. 'x' é tratado aqui também pois é um operador
# formado por uma letra (multiplicação), e precisa do mesmo
# tratamento de prioridade que as demais palavras reservadas.
reserved = {
    "elgio": "ELGIO",
    "DECIMAL": "DECIMAL",
    "_Z_": "Z",
    "_NEG_": "NEG",
    "EXP": "EXP",
    "RESTO": "RESTO",
    "enquanto": "ENQUANTO",
    "se": "SE",
    "entao": "ENTAO",
    "senao": "SENAO",
    "para": "PARA",
    "inicio": "INICIO",
    "fim": "FIM",
    "maior": "MAIOR",
    "menor": "MENOR",
    "igual": "IGUAL",
    "diferente": "DIFERENTE",
    "migual": "MIGUAL",
    "MIgual": "MIGUAL_CAP",
    "x": "MULT",
}

tokens = (
    "ID",
    "FUNCID",
    "NUMBER",
    "ASSIGN",
    "PLUS",
    "MINUS",
    "DIV",
    "DOT",
    "LPAREN",
    "RPAREN",
    "COMMA",
) + tuple(sorted(set(reserved.values())))

# Identificador formal: consoante maiúscula no início, apenas letras,
# termina em letra minúscula, comprimento mínimo de 4 caracteres.
_IDENTIFIER_RE = re.compile(r"^[BCDFGHJKLMNPQRSTVWXYZ][A-Za-z]*[a-z]$")


def _is_valid_identifier(name):
    return len(name) >= 4 and bool(_IDENTIFIER_RE.match(name))


# Erros léxicos acumulados durante a última chamada a `tokenize`.
lexical_errors = []

t_ignore = " \t\r"

t_ASSIGN = r"="
t_PLUS = r"\+"
t_MINUS = r"-"
t_DIV = r"/"
t_DOT = r"\."
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_COMMA = r","


def t_COMMENT(t):
    r"\*[^\n]*"
    # Comentário: do '*' até o fim da linha. Não gera token.


def t_FUNCID(t):
    r"\$[A-Za-z_][A-Za-z0-9_]*"
    name = t.value[1:]
    if not _is_valid_identifier(name):
        lexical_errors.append(
            (t.lexer.lineno, f"nome de função inválido: '{t.value}'")
        )
        return None
    t.type = "FUNCID"
    return t


def t_ID(t):
    r"[A-Za-z_][A-Za-z0-9_]*"
    if t.value in reserved:
        t.type = reserved[t.value]
        return t
    if _is_valid_identifier(t.value):
        t.type = "ID"
        return t
    lexical_errors.append(
        (t.lexer.lineno, f"identificador inválido: '{t.value}'")
    )
    return None


def t_NUMBER(t):
    r"[0-9]+"
    if re.match(r"^[1-9][0-9]*$", t.value):
        t.value = int(t.value)
        return t
    lexical_errors.append(
        (t.lexer.lineno, f"número inválido (zero à esquerda ou zero isolado): '{t.value}'")
    )
    return None


def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)


def t_error(t):
    lexical_errors.append(
        (t.lexer.lineno, f"caractere inválido: '{t.value[0]}'")
    )
    t.lexer.skip(1)


lexer = lex.lex()


def tokenize(source):
    """Executa a análise léxica sobre `source`.

    Retorna uma tupla (tokens, tabela_de_simbolos, erros), em que
    `tokens` é a lista de tokens reconhecidos (na ordem em que
    aparecem), `tabela_de_simbolos` é uma SymbolTable preenchida com
    todo ID/FUNCID encontrado e `erros` é a lista de erros léxicos,
    cada um como (linha, mensagem).
    """
    global lexical_errors
    lexical_errors = []

    symbol_table = SymbolTable()

    lexer.lineno = 1
    lexer.input(source)

    collected = []
    while True:
        tok = lexer.token()
        if tok is None:
            break
        collected.append(tok)
        if tok.type in ("ID", "FUNCID"):
            symbol_table.add(tok.value, tok.type, tok.lineno)

    return collected, symbol_table, list(lexical_errors)
