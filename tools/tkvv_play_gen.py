# -*- coding: utf-8 -*-
"""Bake content demo player: 8 frame 160x120 PNG-sequence -> TKVV.

Content: nen navy + ball trang r=10 + vuong do 20px (PNG trung gian dung
PIL de dung chuan 'PNG-sequence ingest': render PNG -> doc lai PNG ->
encode TKVV). f0=I, con lai P. Ground truth: rgb sum + 16px dau/cuoi.

  python3 tools/tkvv_play_gen.py  ->  writes TkvUI.TkvvPlay.tkv (UTF-8)
"""
import os
from PIL import Image

W = 160
H = 120
T = 8
NFR = 8
PAL = [(16, 24, 64), (255, 255, 255), (200, 30, 30)]
DELAY = 10


def render_png(fi):
    im = Image.new('RGB', (W, H), PAL[0])
    px = im.load()
    cx, cy, r = 30 + fi * 14, 40 + fi * 8, 10
    for y in range(max(0, cy - r), min(H, cy + r + 1)):
        for x in range(max(0, cx - r), min(W, cx + r + 1)):
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= r * r:
                px[x, y] = PAL[1]
    sx, sy = 120 - fi * 8, 30 + fi * 6
    for y in range(max(0, sy), min(H, sy + 20)):
        for x in range(max(0, sx), min(W, sx + 20)):
            px[x, y] = PAL[2]
    return im


def closest(px):
    best, bd = 0, 1 << 30
    for i, c in enumerate(PAL):
        d = (px[0] - c[0]) ** 2 + (px[1] - c[1]) ** 2 + (px[2] - c[2]) ** 2
        if d < bd:
            bd, best = d, i
    return best


def tiles_of(px):
    out = []
    for ty in range(H // T):
        for tx in range(W // T):
            t = []
            for y in range(T):
                for x in range(T):
                    t.append(px[(ty * T + y) * W + tx * T + x])
            out.append(t)
    return out


def u16(v):
    return bytes([v & 0xFF, (v >> 8) & 0xFF])


def u32(v):
    return bytes([v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF])


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frames = []
    for fi in range(NFR):
        im = render_png(fi)
        im.save(os.path.join(root, 'build', 'play_f%d.png' % fi))
        # PNG-sequence ingest: doc lai PNG nhu input ngoai
        back = Image.open(os.path.join(root, 'build', 'play_f%d.png' % fi)).convert('RGB')
        assert back.size == (W, H)
        frames.append([closest(back.getpixel((x, y))) for y in range(H) for x in range(W)])
    gts = []
    for px in frames:
        rgb = []
        for idx in px:
            rgb = rgb + list(PAL[idx])
        gts.append({'sum': sum(rgb), 'first': rgb[:48], 'last': rgb[-48:]})
    payloads = []
    ftypes = []
    prev_tiles = None
    for fi, px in enumerate(frames):
        tiles = tiles_of(px)
        if fi == 0:
            ftypes.append(0)
            p = bytearray()
            for t in tiles:
                p = p + bytes(t)
            payloads.append(bytes(p))
        else:
            ftypes.append(1)
            changed = [ti for ti in range(len(tiles)) if tiles[ti] != prev_tiles[ti]]
            p = bytearray()
            p = p + u16(len(changed))
            for ti in changed:
                p = p + u16(ti) + bytes(tiles[ti])
            payloads.append(bytes(p))
        prev_tiles = tiles
    head_len = 4 + 2 * 5 + len(PAL) * 3 + NFR * 2 + NFR * 9
    off = head_len
    table = bytearray()
    for fi in range(NFR):
        table = table + bytes([ftypes[fi]]) + u32(off) + u32(len(payloads[fi]))
        off = off + len(payloads[fi])
    blob = (b'TKVV' + u16(1) + u16(W) + u16(H) + u16(NFR) + u16(len(PAL)))
    for c in PAL:
        blob = blob + bytes(c)
    for _ in range(NFR):
        blob = blob + u16(DELAY)
    blob = blob + bytes(table)
    for p in payloads:
        blob = blob + bytes(p)
    assert len(blob) == off, (len(blob), off)
    print('TKVV-PLAY: %dx%d x%d, %d bytes (raw %d, ratio %.2f)' %
          (W, H, NFR, len(blob), W * H * NFR, W * H * NFR / len(blob)))
    print('  payloads:', [len(p) for p in payloads])
    for i, g in enumerate(gts):
        print('  f%d sum=%d' % (i, g['sum']))

    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""TkvUI.TkvvPlay - content demo player bake san (sinh boi tools/tkvv_play_gen.py).')
    L.append('')
    L.append('160x120 ball+square 8 frames qua PNG trung gian (mau ingest PNG-sequence).')
    L.append('Ground truth: rgb sum + 16px dau/cuoi/frame. Khong doc file luc chay.')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    L.append('def tkvp_len() -> "i32":')
    L.append('    return %d' % len(blob))
    L.append('')
    L.append('def tkvp_bytes() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in blob))
    L.append('')
    L.append('def tkvp_nframes() -> "i32":')
    L.append('    return %d' % NFR)
    L.append('')
    for i, g in enumerate(gts):
        L.append('def tkvp_f%d_sum() -> "i32":' % i)
        L.append('    return %d' % g['sum'])
        L.append('')
    out = os.path.join(root, 'TkvUI.TkvvPlay.tkv')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out)


if __name__ == '__main__':
    main()
