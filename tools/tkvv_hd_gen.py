# -*- coding: utf-8 -*-
"""Bake content 320x240 cho do toc fast-path TKVV (verdict HD realtime).

Content: nen navy phang + ball trang r=24 + vuong do 40x40 di chuyen,
4 frames delay 10cs (f0=I, f1..f3=P). Chunked 16 phan de compiler nuot.
Ground truth: rgb sum + 16px dau/cuoi/frame + so tiles changed/frame.

  python3 tools/tkvv_hd_gen.py  ->  appends TkvUI.TkvvHDData.tkv? KHONG -
  writes TkvUI.TkvvHD.tkv (rieng, de khoi lam nang module unit nho).
"""
import os

W = 320
H = 240
T = 8
NFR = 4
PAL = [(16, 24, 64), (255, 255, 255), (200, 30, 30)]
DELAY = 10
NCH = 16


def render(fi):
    cx = 40 + fi * 30
    cy = 60 + fi * 20
    sx = 200 - fi * 20
    sy = 150 - fi * 10
    px = []
    for y in range(H):
        for x in range(W):
            v = 0
            dx, dy = x - cx, y - cy
            if dx * dx + dy * dy <= 24 * 24:
                v = 1
            if sx <= x < sx + 40 and sy <= y < sy + 40:
                v = 2
            px.append(v)
    return px


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
    frames = [render(i) for i in range(NFR)]
    gts = []
    for px in frames:
        rgb = []
        for idx in px:
            rgb = rgb + list(PAL[idx])
        gts.append({'sum': sum(rgb), 'first': rgb[:48], 'last': rgb[-48:]})
    payloads = []
    ftypes = []
    prev_tiles = None
    nchanged = []
    for fi, px in enumerate(frames):
        tiles = tiles_of(px)
        if fi == 0:
            ftypes.append(0)
            p = bytearray()
            for t in tiles:
                p = p + bytes(t)
            payloads.append(bytes(p))
            nchanged.append(len(tiles))
        else:
            ftypes.append(1)
            changed = [ti for ti in range(len(tiles)) if tiles[ti] != prev_tiles[ti]]
            nchanged.append(len(changed))
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
    print('TKVV-HD: %dx%d x%d, %d bytes total' % (W, H, NFR, len(blob)))
    print('  payloads:', [len(p) for p in payloads], 'changed tiles:', nchanged)
    print('  raw would be:', W * H * NFR)
    for i, g in enumerate(gts):
        print('  f%d sum=%d' % (i, g['sum']))

    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""TkvUI.TkvvHD - content 320x240 cho do toc fast-path (sinh boi tools/tkvv_hd_gen.py).')
    L.append('')
    L.append('Bake chunked (compiler khoi nghen). Ground truth: sum + 16px dau/cuoi.')
    L.append('Khong doc file luc chay. Chi dung do fps, khong vao suite nang.')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    flat = bytes(blob)
    per = (len(flat) + NCH - 1) // NCH
    for i in range(NCH):
        part = flat[i * per:(i + 1) * per]
        L.append('def tkhd_part%d() -> "list[i32]":' % i)
        L.append('    return [%s]' % ', '.join(str(x) for x in part))
        L.append('')
    L.append('def tkhd_len() -> "i32":')
    L.append('    return %d' % len(flat))
    L.append('')
    L.append('def tkhd_nframes() -> "i32":')
    L.append('    return %d' % NFR)
    L.append('')
    for i, g in enumerate(gts):
        L.append('def tkhd_f%d_sum() -> "i32":' % i)
        L.append('    return %d' % g['sum'])
        L.append('')
    L.append('def tkhd_bytes(out: "list[i32]") -> "i32":')
    for i in range(NCH):
        L.append('    p%d = tkhd_part%d()' % (i, i))
        L.append('    k%d = int(0)' % i)
        L.append('    while k%d < len(p%d):' % (i, i))
        L.append('        out.append(p%d[k%d])' % (i, i))
        L.append('        k%d = k%d + 1' % (i, i))
    L.append('    return len(out)')
    L.append('')
    out = os.path.join(root, 'TkvUI.TkvvHD.tkv')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out)


if __name__ == '__main__':
    main()
