# -*- coding: utf-8 -*-
"""Bake monochrome 12x12 symbol glyphs from Segoe UI Symbol into TkvUI.EmojiData.tkv.

Pattern follows I18nData (bake offline, no file I/O at runtime - compiler gap):
  python3 tools/emoji_gen.py  ->  writes TkvUI.EmojiData.tkv (UTF-8)

Source font: C:/Windows/Fonts/seguisym.ttf (monochrome outlines for BMP symbols).
Method: render at 48px with PIL, tight-crop, scale longest side to 12px
(LANCZOS), center in 12x12 cell, threshold at 128 -> 1bpp rows (12-bit ints).

Glyph set (12 BMP symbols, all present in Segoe UI Symbol):
  U+2600 sun, U+2605 star, U+2665 heart, U+2714 check, U+2716 cross,
  U+25B6 play, U+25CF circle, U+25A0 square, U+25B2 tri-up, U+266A note,
  U+263A smile, U+25BC tri-down.
"""
import os

CPS = [0x2600, 0x2605, 0x2665, 0x2714, 0x2716, 0x25B6,
       0x25CF, 0x25A0, 0x25B2, 0x266A, 0x263A, 0x25BC]
NAMES = ['sun', 'star', 'heart', 'check', 'cross', 'play',
         'circle', 'square', 'triup', 'note', 'smile', 'tridown']
FONT = 'C:/Windows/Fonts/seguisym.ttf'
W = 12
H = 12


def rasterize(cp):
    from PIL import Image, ImageFont
    f48 = ImageFont.truetype(FONT, 48)
    ch = chr(cp)
    m = f48.getmask(ch)
    bbox = m.getbbox()
    if bbox is None:
        raise SystemExit('empty glyph U+%04X' % cp)
    img = Image.new('L', m.size, 0)
    img.putdata(list(m))
    crop = img.crop(bbox)
    w, h = crop.size
    s = 12.0 / max(w, h)
    nw = max(1, int(w * s + 0.5))
    nh = max(1, int(h * s + 0.5))
    small = crop.resize((nw, nh), Image.LANCZOS)
    cell = Image.new('L', (W, H), 0)
    cell.paste(small, ((W - nw) // 2, (H - nh) // 2))
    px = cell.load()
    rows = []
    for y in range(H):
        bits = 0
        for x in range(W):
            bits = bits * 2 + (1 if px[x, y] >= 128 else 0)
        rows.append(bits)
    ink = sum(bin(r).count('1') for r in rows)
    if ink < 10:
        raise SystemExit('glyph U+%04X too faint (ink=%d)' % (cp, ink))
    return rows, ink


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    all_rows = []
    for cp, nm in zip(CPS, NAMES):
        rows, ink = rasterize(cp)
        all_rows.append(rows)
        print('U+%04X %-7s ink=%3d' % (cp, nm, ink))
    # pairwise distinctness guard
    seen = set()
    for i, rows in enumerate(all_rows):
        key = tuple(rows)
        if key in seen:
            raise SystemExit('duplicate glyph at index %d' % i)
        seen.add(key)
    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""TkvUI.EmojiData - baked monochrome 12x12 symbol glyphs (sinh boi tools/emoji_gen.py).')
    L.append('')
    L.append('Nguon: Segoe UI Symbol (glyph don sac cho BMP symbols), bake offline')
    L.append('qua PIL (render 48px -> crop -> scale ve 12px -> threshold 128).')
    L.append('Khong doc file luc chay (ne compiler gap file I/O, giong I18nData).')
    L.append('')
    L.append('Moi glyph: 12 hang x 12 bit (int 0..4095, bit cao = pixel trai).')
    L.append('Ve bang emoji_blit (mask 1bpp + mau truyen vao, giong vi_draw_bits).')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    L.append('EMOJI_W = 12')
    L.append('EMOJI_H = 12')
    L.append('')
    L.append('def emoji_count() -> "i32":')
    L.append('    return %d' % len(CPS))
    L.append('')
    L.append('def emoji_codepoint(seq: "str") -> "i32":')
    for cp in CPS:
        L.append('    if seq == "%s":' % chr(cp))
        L.append('        return %d' % cp)
    L.append('    return -1')
    L.append('')
    L.append('def emoji_slot_for(cp: "i32") -> "i32":')
    for i, cp in enumerate(CPS):
        L.append('    if cp == %d:' % cp)
        L.append('        return %d' % i)
    L.append('    return -1')
    L.append('')
    L.append('def emoji_rows(slot: "i32") -> "list[i32]":')
    for i, rows in enumerate(all_rows):
        L.append('    if slot == %d:' % i)
        L.append('        return [%s]' % ', '.join(str(r) for r in rows))
    L.append('    return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]')
    L.append('')
    L.append('def emoji_row_bits(slot: "i32", row: "i32") -> "i32":')
    L.append('    if slot < 0 or slot >= %d:' % len(CPS))
    L.append('        return 0')
    L.append('    if row < 0 or row >= 12:')
    L.append('        return 0')
    L.append('    rows = emoji_rows(slot)')
    L.append('    return rows[row]')
    L.append('')
    L.append('def emoji_ink(slot: "i32") -> "i32":')
    L.append('    # So pixel ink cua glyph (cho test distinct/nonzero).')
    L.append('    rows = emoji_rows(slot)')
    L.append('    n = int(0)')
    L.append('    r = int(0)')
    L.append('    while r < 12:')
    L.append('        v = rows[r]')
    L.append('        c = int(0)')
    L.append('        while v > 0:')
    L.append('            n = n + v % 2')
    L.append('            v = v // 2')
    L.append('        r = r + 1')
    L.append('    return n')
    L.append('')
    L.append('def emoji_blit(buf: "list[i64]", surf: "PixelSurface", slot: "i32", x: "i32", y: "i32", color: "ColorRgba") -> "i32":')
    L.append('    # Ve 1 glyph 12x12 tai (x, y) theo mask 1bpp. Tra chieu rong 12.')
    L.append('    if slot < 0 or slot >= %d:' % len(CPS))
    L.append('        return 0')
    L.append('    rows = emoji_rows(slot)')
    L.append('    r = int(0)')
    L.append('    while r < 12:')
    L.append('        bits = rows[r]')
    L.append('        c = int(0)')
    L.append('        while c < 12:')
    L.append('            on = bits // 2048')
    L.append('            bits = bits % 2048')
    L.append('            bits = bits * 2')
    L.append('            if on == 1:')
    L.append('                surface_blend_pixel(buf, surf, x + c, y + r, color)')
    L.append('            c = c + 1')
    L.append('        r = r + 1')
    L.append('    return 12')
    L.append('')
    L.append('# =========================================================')
    L.append('# SELFTEST')
    L.append('# =========================================================')
    L.append('def emojicheck(acc: "list[i32]", name: "str", ok: "i32") -> "i32":')
    L.append('    acc[1] = acc[1] + 1')
    L.append('    if ok == 1:')
    L.append('        acc[0] = acc[0] + 1')
    L.append('        print("  PASS " + name)')
    L.append('        return 1')
    L.append('    print("  FAIL " + name)')
    L.append('    return 0')
    L.append('')
    L.append('def emojicheck_i(acc: "list[i32]", name: "str", got: "i32", want: "i32") -> "i32":')
    L.append('    acc[1] = acc[1] + 1')
    L.append('    if got == want:')
    L.append('        acc[0] = acc[0] + 1')
    L.append('        print("  PASS " + name + " = " + str(got))')
    L.append('        return 1')
    L.append('    print("  FAIL " + name + " got=" + str(got) + " want=" + str(want))')
    L.append('    return 0')
    L.append('')
    L.append('def emoji_selftest() -> "str":')
    L.append('    print("== TkvUI.EmojiData selftest ==")')
    L.append('    acc = [int(0), int(0)]')
    L.append('    emojicheck_i(acc, "count", emoji_count(), %d)' % len(CPS))
    for i, cp in enumerate(CPS):
        L.append('    emojicheck_i(acc, "slot U+%04X", emoji_slot_for(%d), %d)' % (cp, cp, i))
    for i, cp in enumerate(CPS):
        L.append('    emojicheck_i(acc, "cp %s", emoji_codepoint("%s"), %d)' % (NAMES[i], chr(cp), cp))
    L.append('    emojicheck_i(acc, "cp miss", emoji_codepoint("AB"), -1)')
    L.append('    emojicheck_i(acc, "slot miss", emoji_slot_for(128512), -1)')
    L.append('    emojicheck_i(acc, "row oob", emoji_row_bits(0, 12), 0)')
    L.append('    emojicheck_i(acc, "slot oob", emoji_row_bits(99, 0), 0)')
    L.append('    i = int(0)')
    L.append('    while i < %d:' % len(CPS))
    L.append('        ok = 0')
    L.append('        if emoji_ink(i) > 0:')
    L.append('            ok = 1')
    L.append('        emojicheck(acc, "ink " + str(i), ok)')
    L.append('        i = i + 1')
    L.append('    a = int(0)')
    L.append('    while a < %d:' % len(CPS))
    L.append('        b = a + 1')
    L.append('        while b < %d:' % len(CPS))
    L.append('            same = 1')
    L.append('            r = int(0)')
    L.append('            while r < 12:')
    L.append('                if emoji_row_bits(a, r) != emoji_row_bits(b, r):')
    L.append('                    same = 0')
    L.append('                r = r + 1')
    L.append('            okd = 0')
    L.append('            if same == 0:')
    L.append('                okd = 1')
    L.append('            emojicheck(acc, "distinct " + str(a) + "/" + str(b), okd)')
    L.append('            b = b + 1')
    L.append('        a = a + 1')
    L.append('    print("emojidata: " + str(acc[0]) + "/" + str(acc[1]))')
    L.append('    if acc[0] == acc[1]:')
    L.append('        return "EMOJIDATA_OK"')
    L.append('    return "EMOJIDATA_FAIL"')
    L.append('')
    out = os.path.join(root, 'TkvUI.EmojiData.tkv')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out)


if __name__ == '__main__':
    main()
