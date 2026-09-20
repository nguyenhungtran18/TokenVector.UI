with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add return type to first fb_draw_run_emoji
content = content.replace(
    'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color):',
    'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color) -> "i32":'
)

# Fix 2: Remove the duplicate fb_draw_run_emoji (second occurrence)
# Find the second occurrence and remove it
parts = content.split('def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color):')
if len(parts) >= 3:
    # Keep first part + first function, remove second function entirely
    first_part = parts[0] + 'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color) -> "i32":' + parts[1]
    # Find the second function and remove it
    second_part = parts[2]
    second_func_end = parts[2].find('def fb_draw_run_color')
    if second_func_end >= 0:
        content = parts[0] + 'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color) -> "i32":' + parts[1] + parts[2][second_func_end:]
    else:
        content = parts[0] + 'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color) -> "i32":' + parts[1] + parts[2]
else:
    # Fallback: just replace the first occurrence
    content = content.replace(
        'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color):',
        'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color) -> "i32":',
        1  # Only replace first occurrence
    )

# Fix fb_draw_run_color return type
content = content.replace(
    'def fb_draw_run_color(buf, surf, text, start, ulen, x, y, color):',
    'def fb_draw_run_color(buf, surf, text, start, ulen, x, y, color) -> "i32":'
)

# Update fb_font_name to include emoji and color
old_font_name = '''def fb_font_name(font: "i32") -> "str":
    if font == 1:
        return "viet"
    if font == 2:
        return "i18n"
    if font == 3:
        return "missing"
    return "text"'''

new_font_name = '''def fb_font_name(font: "i32") -> "str":
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
    return "text"'''

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