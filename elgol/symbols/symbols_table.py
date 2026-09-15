class SymbolTable:

    def __init__(self):
        self.symbols = {}

    def add(self, name, token_type):
        self.symbols[name] = token_type

    def exists(self, name):
        return name in self.symbols

    def get(self, name):
        return self.symbols.get(name)