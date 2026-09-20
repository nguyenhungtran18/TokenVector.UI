with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

# Add return type to fb_draw_run_emoji
content = content.replace(
    'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color):',
    'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color) -> "i32":'
)

# Remove duplicate fb_draw_run_emoji (keep first, remove second)
content = content.replace(
'''def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color):
    end = start + ulen
    idx = start
    cx = x
    while idx < end:
        adv = utf8_seq_len(text, idx)
        if idx + adv > end:
            adv = end - idx
        r = Rect2D(cx, y, 12, 12)
        _ = fill_round_rect(buf, surf, r, 2, ColorRgba(255, 255, 255, 255))
        draw_string(buf, surf, "E", cx + 2, y + 2, 1, ColorRgba(0, 0, 0, 255))
        adv = utf8_seq_len(text, idx)
        if idx + adv > end:
            adv = end - idx
        cx = cx + 12
        idx = idx + adv
    return cx - x

def fb_draw_run_color(buf, surf, text, start, ulen, x, y, color):''',
'def fb_draw_run_color(buf, surf, text, start, ulen, x, y, color) -> "i32":')

# Add return type to fb_font_name
content = content.replace(
'''def fb_font_name(font: "i32") -> "str":
    if font == 1:
        return "viet"
    if font == 2:
        return "i18n"
    if font == 3:
        return "missing"
    return "text"''',
'''def fb_font_name(font: "i32") -> "str":
    if font == 1:
        return "viet"
    if font == 2:
        return "i18n"
    if font == 3:
        return "missing"
    if font == 4:
        return "emoji"
    if font == 5:
        return "color"
    return "text"''')

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')