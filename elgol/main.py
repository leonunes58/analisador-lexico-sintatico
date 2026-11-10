import argparse
import sys
from pathlib import Path

from analyzer import analyze


def print_tokens(result):
    print("=== TOKENS ===")
    for tok in result.tokens:
        print(f"linha {tok.lineno:>3}  {tok.type:<12} {tok.value!r}")


def print_symbols(result):
    print("\n=== TABELA DE SIMBOLOS ===")
    if len(result.symbol_table) == 0:
        print("(vazia)")
    for name, info in result.symbol_table:
        print(f"{name:<15} tipo={info['type']:<8} linhas={info['lines']}")


def print_errors(title, errors):
    print(f"\n=== {title} ===")
    if not errors:
        print("nenhum erro encontrado")
    for lineno, message in errors:
        where = f"linha {lineno}" if lineno is not None else "final do arquivo"
        print(f"{where}: {message}")


def print_tree(result):
    print("\n=== ARVORE SINTATICA ===")
    if result.tree is None:
        print("(não gerada: o programa não pôde ser reconhecido)")
        return
    print("\n".join(result.tree.pretty()))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Analisador léxico e sintático da linguagem Elgol")
    ap.add_argument("arquivo", help="arquivo-fonte .elgol")
    ap.add_argument("--sem-tokens", action="store_true", help="não imprime a lista de tokens")
    ap.add_argument("--sem-arvore", action="store_true", help="não imprime a árvore sintática")
    args = ap.parse_args(argv)

    source = Path(args.arquivo).read_text(encoding="utf-8")
    result = analyze(source)

    if not args.sem_tokens:
        print_tokens(result)
    print_symbols(result)
    print_errors("ERROS LEXICOS", result.lexical_errors)
    print_errors("ERROS SINTATICOS", result.syntax_errors)
    if not args.sem_arvore and result.ok:
        print_tree(result)

    print("\nRESULTADO:", "programa VÁLIDO" if result.ok else "programa INVÁLIDO")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
