with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def fbcheck_f(acc, name, got, want, tol):',
    'def fbcheck_f(acc, name, got, want, tol) -> "i32":'
)

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')