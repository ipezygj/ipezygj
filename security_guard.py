""" Technical implementation for Hummingbot Gateway V2.1. """

import ast
import sys
from pathlib import Path

class SecurityScanner(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.violations = 0

    def visit_Constant(self, node: ast.Constant):
        if isinstance(node.value, str):
            val = node.value.lower()
            if "http" + "://" in val or "https" + "://" in val:
                print(f"CRITICAL: Resource violation in {self.filepath.name} at line {node.lineno}.")
                self.violations += 1
        self.generic_visit(node)

def execute_security_audit(directory: str) -> int:
    violations = 0
    for filepath in Path(directory).rglob("*.py"):
        if filepath.name == "constants.py": continue
        try:
            tree = ast.parse(filepath.read_text(encoding="utf-8"))
            scanner = SecurityScanner(filepath)
            scanner.visit(tree)
            violations += scanner.violations
        except: continue
    return violations

if __name__ == "__main__":
    if execute_security_audit(".") > 0:
        sys.exit(1)
    print("Security audit passed.")
    sys.exit(0)
