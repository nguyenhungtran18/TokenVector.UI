import ast
import sys

with open('examples/TkvUI.Fuzz.tkv', 'r', encoding='utf-8') as f:
    code = f.read()

try:
    ast.parse(code)
    print('Syntax OK')
except SyntaxError as e:
    print(f'Syntax error at line {e.lineno}: {e.msg}')
    with open('examples/TkvUI.Fuzz.tkv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        if e.lineno <= len(lines):
            print(f'Line {e.lineno}: {lines[e.lineno-1].rstrip()}')