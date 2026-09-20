with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def fb_resolve(text: "str", starts, lens, fonts) -> "i32":',
    'def fb_resolve(text: "str", starts: "list", lens: "list", fonts: "list") -> "i32":'
)

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')