"""Roteiro de demonstração: roda o analisador em todos os exemplos e mostra um resumo.

uso:
    python3 demo.py            # resumo de todos os exemplos
    python3 demo.py -v         # mostra os erros encontrados em cada arquivo incorreto
    python3 demo.py --arvore   # imprime também a árvore dos programas corretos
"""
import argparse
from pathlib import Path

from analyzer import analyze

BASE = Path(__file__).parent / "tests"
GRUPOS = [
    ("CORRETOS (devem ser aceitos)", True, [BASE / "correto.elgol"] + sorted((BASE / "exemplos" / "corretos").glob("*.elgol"))),
    ("INCORRETOS (devem ser rejeitados)", False, [BASE / "incorreto.elgol"] + sorted((BASE / "exemplos" / "incorretos").glob("*.elgol"))),
]


def descricao(path):
    first = path.read_text(encoding="utf-8").splitlines()[0]
    return first.lstrip("* ").strip() if first.startswith("*") else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--verboso", action="store_true")
    ap.add_argument("--arvore", action="store_true")
    args = ap.parse_args()

    total = acertos = 0
    for titulo, deve_passar, arquivos in GRUPOS:
        print(f"\n{'=' * 70}\n {titulo}\n{'=' * 70}")
        for path in arquivos:
            result = analyze(path.read_text(encoding="utf-8"))
            correto = result.ok == deve_passar
            total += 1
            acertos += correto
            status = "OK  " if correto else "FALHOU"
            veredito = "aceito" if result.ok else (
                f"rejeitado ({len(result.lexical_errors)} léxico(s), {len(result.syntax_errors)} sintático(s))"
            )
            print(f"[{status}] {path.name:<34} {veredito}")
            print(f"         {descricao(path)}")
            if args.verboso and not result.ok:
                for tipo, errs in (("léxico", result.lexical_errors), ("sintático", result.syntax_errors)):
                    for lineno, msg in errs:
                        onde = f"linha {lineno}" if lineno is not None else "fim do arquivo"
                        print(f"           - {tipo}, {onde}: {msg}")
            if args.arvore and result.ok:
                print("\n".join("           " + l for l in result.tree.pretty()))

    print(f"\n{acertos}/{total} exemplos com o resultado esperado")
    return 0 if acertos == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
