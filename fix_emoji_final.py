with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color):',
    'def fb_draw_run_emoji(buf, surf, text: "str", start: "i32", ulen: "i32", x: "i32", y: "i32", color: "ColorRgba") -> "i32":'
)

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')