from dataclasses import dataclass, field

from lexer.lexer import tokenize
from syntax.parser import parse


@dataclass
class AnalysisResult:
    tokens: list
    symbol_table: object
    lexical_errors: list = field(default_factory=list)
    syntax_errors: list = field(default_factory=list)
    tree: object = None

    @property
    def ok(self):
        return not self.lexical_errors and not self.syntax_errors


def analyze(source):
    tokens, symbol_table, lexical_errors = tokenize(source)
    tree, syntax_errors = parse(tokens)
    return AnalysisResult(
        tokens=tokens,
        symbol_table=symbol_table,
        lexical_errors=lexical_errors,
        syntax_errors=syntax_errors,
        tree=tree,
    )
