class Node:

    def __init__(self, kind, children=None, value=None, lineno=None):
        self.kind = kind
        self.children = [c for c in (children or []) if c is not None]
        self.value = value
        self.lineno = lineno

    def label(self):
        if self.value is None:
            return self.kind
        return f"{self.kind} ({self.value})"

    def pretty(self, prefix="", is_last=True, is_root=True):
        lines = []
        if is_root:
            lines.append(self.label())
            child_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            lines.append(prefix + connector + self.label())
            child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            last = i == len(self.children) - 1
            lines.extend(child.pretty(child_prefix, last, is_root=False))
        return lines

    def __repr__(self):
        return f"Node({self.kind!r}, value={self.value!r}, children={len(self.children)})"
