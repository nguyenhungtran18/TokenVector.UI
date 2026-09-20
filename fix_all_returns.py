with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all missing return type annotations
replacements = [
    ('def fbcheck_i(acc, name, got, want):', 'def fbcheck_i(acc, name, got, want) -> "i32":'),
    ('def fbcheck_f(acc, name, got, want, tol):', 'def fbcheck_f(acc, name, got, want, tol) -> "i32":'),
    ('def fbcheck_s(acc, name, got, want):', 'def fbcheck_s(acc, name, got, want) -> "i32":'),
    ('def fbcheck(acc, name, ok):', 'def fbcheck(acc, name, ok) -> "i32":'),
    ('def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color):', 'def fb_draw_run_emoji(buf, surf, text, start, ulen, x, y, color) -> "i32":'),
    ('def fb_draw_run_color(buf, surf, text, start, ulen, x, y, color):', 'def fb_draw_run_color(buf, surf, text, start, ulen, x, y, color) -> "i32":'),
    ('def fb_count_missing(text):', 'def fb_count_missing(text) -> "i32":'),
    ('def fb_has_font(text, font):', 'def fb_has_font(text, font) -> "i32":'),
    ('def fb_resolve(text, starts, lens, fonts):', 'def fb_resolve(text, starts, lens, fonts) -> "i32":'),
    ('def fb_draw_string(buf, surf, abuf, atlas, iabuf, iatlas, text, x, y, color):', 'def fb_draw_string(buf, surf, abuf, atlas, iabuf, iatlas, text, x, y, color) -> "i32":'),
    ('def fb_draw_string(buf, surf, abuf, atlas, iabuf, iatlas, text, x, y, color):', 'def fb_draw_string(buf, surf, abuf, atlas, iabuf, iatlas, text, x, y, color) -> "i32":'),
    ('def fb_check(acc, name, ok):', 'def fb_check(acc, name, ok) -> "i32":'),
    ('def fbcheck_i(acc, name, got, want):', 'def fbcheck_i(acc, name, got, want) -> "i32":'),
    ('def fbcheck_f(acc, name, got, want, tol):', 'def fbcheck_f(acc, name, got, want, tol) -> "i32":'),
    ('def fbcheck_s(acc, name, got, want):', 'def fbcheck_s(acc, name, got, want) -> "i32":'),
    ('def fb_check(acc, name, ok):', 'def fb_check(acc, name, ok) -> "i32":'),
    ('def fbcheck_i(acc, name, got, want):', 'def fbcheck_i(acc, name, got, want) -> "i32":'),
    ('def fbcheck_f(acc, name, got, want, tol):', 'def fbcheck_f(acc, name, got, want, tol) -> "i32":'),
    ('def fbcheck_s(acc, name, got, want):', 'def fbcheck_s(acc, name, got, want) -> "i32":'),
    ('def fb_check(acc, name, ok):', 'def fb_check(acc, name, ok) -> "i32":'),
    ('def fbcheck_i(acc, name, got, want):', 'def fbcheck_i(acc, name, got, want) -> "i32":'),
    ('def fbcheck_f(acc, name, got, want, tol):', 'def fbcheck_f(acc, name, got, want, tol) -> "i32":'),
    ('def fbcheck_s(acc, name, got, want):', 'def fbcheck_s(acc, name, got, want) -> "i32":'),
]

with open('TkvUI.FontFallback.tkv', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in replacements:
    content = content.replace(old, new)

with open('TkvUI.FontFallback.tkv', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')