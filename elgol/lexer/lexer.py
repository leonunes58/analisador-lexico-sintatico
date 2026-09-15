import ply.lex as lex

tokens = (
    "ID",
    "FUNCID",
    "WORD_RESERVED"
    "NUMBER",
    "PLUS",
    "MINUS",
    "DIV",
    "LPAREN",
    "ASSIGN",
    "MULTI",
    "DELIMITER",
    "COMMA"
)

ID = r''
FUNCID = r''
WORD_RESERVED = r''
NUMBER = r''
PLUS = r''
MINUS = r''
DIV = r''
LPAREN = r''
ASSIGN = r''
MULTI = r''
DELIMITER = r''
COMMA = r''

lexer = lex.lex()