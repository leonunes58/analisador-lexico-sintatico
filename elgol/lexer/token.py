from enum import Enum


class TokenType(Enum):
    ID = 'ID'
    FUNCID = 'FUNCID'
    WORD_RESERVED = 'WORD_RESERVED'
    NUMBER = 'NUMBER'
    PLUS = 'PLUS'
    MINUS = 'MINUS'
    DIV = 'DIV'
    LPAREN = 'LPAREN'
    ASSIGN = 'ASSIGN'
    MULTI = 'MULTI'
    DELIMITER = 'DELIMITER'
    COMMA = 'COMMA'