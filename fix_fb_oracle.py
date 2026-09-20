with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def fb_oracle(seq):',
    'def fb_oracle(seq) -> "i32":'
)

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')