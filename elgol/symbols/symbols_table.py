class SymbolTable:

    def __init__(self):
        self.symbols = {}

    def add(self, name, token_type, lineno):
        entry = self.symbols.setdefault(name, {"type": token_type, "lines": []})
        entry["lines"].append(lineno)

    def exists(self, name):
        return name in self.symbols

    def get(self, name):
        return self.symbols.get(name)

    def __iter__(self):
        return iter(self.symbols.items())

    def __len__(self):
        return len(self.symbols)
