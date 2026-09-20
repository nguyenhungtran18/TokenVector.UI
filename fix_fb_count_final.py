with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def fb_count_missing(text) -> "i32":',
    'def fb_count_missing(text: "str") -> "i32":'
)

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')