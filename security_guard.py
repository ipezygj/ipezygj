import ast
import sys
from pathlib import Path

# Perus tarkistus URL-osoitteille
for p in Path('.').rglob('*.py'):
    if p.name == 'constants.py': continue
    with open(p, 'r') as f:
        t = ast.parse(f.read())
        for n in ast.walk(t):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                if 'http' in n.value.lower():
                    print(f"Löytyi osoite: {p} rivi {n.lineno}")
                    sys.exit(1)
print("Kaikki ok")
