from lexer.lexer import lexer

codigo = """
x = 10 + 20;
"""

lexer.input(codigo)

while True:
    token = lexer.token()

    if not token:
        break

    print(token)