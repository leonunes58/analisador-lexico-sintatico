from enum import Enum


class TokenType(Enum):
    # Identificadores e literais
    ID = 'ID'
    FUNCID = 'FUNCID'
    NUMBER = 'NUMBER'

    # Palavras reservadas (cada uma é seu próprio token, pois a
    # linguagem é case-sensitive: migual != MIgual)
    ELGIO = 'ELGIO'
    DECIMAL = 'DECIMAL'
    Z = 'Z'              # _Z_
    NEG = 'NEG'           # _NEG_
    EXP = 'EXP'
    RESTO = 'RESTO'
    ENQUANTO = 'ENQUANTO'
    SE = 'SE'
    ENTAO = 'ENTAO'
    SENAO = 'SENAO'
    PARA = 'PARA'
    INICIO = 'INICIO'
    FIM = 'FIM'
    MAIOR = 'MAIOR'
    MENOR = 'MENOR'
    IGUAL = 'IGUAL'
    DIFERENTE = 'DIFERENTE'
    MIGUAL = 'MIGUAL'
    MIGUAL_CAP = 'MIGUAL_CAP'  # MIgual

    # Operadores e delimitadores
    ASSIGN = 'ASSIGN'    # =
    PLUS = 'PLUS'        # +
    MINUS = 'MINUS'      # -
    DIV = 'DIV'          # /
    MULT = 'MULT'        # x
    DOT = 'DOT'          # .
    LPAREN = 'LPAREN'    # (
    RPAREN = 'RPAREN'    # )
    COMMA = 'COMMA'      # ,
