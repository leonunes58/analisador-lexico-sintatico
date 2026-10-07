import sys
from pathlib import Path

from lexer.lexer import tokenize


def main(argv):
    if len(argv) != 2:
        print("uso: python3 main.py <arquivo.elgol>")
        return 1

    path = Path(argv[1])
    source = path.read_text(encoding="utf-8")

    tokens, symbol_table, errors = tokenize(source)

    print("=== TOKENS ===")
    for tok in tokens:
        print(f"linha {tok.lineno:>3}  {tok.type:<12} {tok.value!r}")

    print("\n=== TABELA DE SIMBOLOS ===")
    if len(symbol_table) == 0:
        print("(vazia)")
    for name, info in symbol_table:
        print(f"{name:<15} tipo={info['type']:<8} linhas={info['lines']}")

    print("\n=== ERROS LEXICOS ===")
    if not errors:
        print("nenhum erro encontrado")
    for lineno, message in errors:
        print(f"linha {lineno}: {message}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
