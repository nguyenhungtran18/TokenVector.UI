with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'def fb_draw_string(buf, surf, abuf, atlas, iabuf, iatlas, text, x, y, color):',
    'def fb_draw_string(buf, surf, abuf, atlas, iabuf, iatlas, text, x, y, color) -> "i32":'
)

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')