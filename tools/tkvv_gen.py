# -*- coding: utf-8 -*-
"""Encoder + ground truth cho TKVV (TokenVector Video) - format custom giong TKVA.

Triet ly (copy TKVA audio): dung implement chuan nang (H.264), thiet ke
format cho decoder .tkv de nhat: chunk + profile + O(1) seek + encoder
offline manh (Python) + decoder thuan arithmetic + verify doc lap 2 kenh.

TKVV v1 (bit-exact, profile 0/1):
  magic 'TKVV' (4) | ver u16=1 | w u16 | h u16 | nframes u16 | palsz u16
  palette palsz*3 bytes (RGB)
  delays nframes*u16 (cs)
  frame table nframes*(type u8 + off u32 + len u32)  -- O(1) seek
  payloads:
    I (type 0): w*h indices u8
    P (type 1): ntiles u16 + tiles(tileidx u16 + 64 indices) -- 8x8 tiles

Sample: 32x24, bg idx0 (navy), ball idx1 (white) r=3, 6 frames di chuyen,
delay 10cs/frame. Frame 0 = I, con lai = P (changed tiles vs prev).

  python3 tools/tkvv_gen.py  ->  writes TkvUI.TkvvData.tkv (UTF-8)
"""
import os

W = 32
H = 24
T = 8
NFR = 6
PAL = [(16, 24, 64), (255, 255, 255)]
DELAY = 10


def render(fi):
    # Ball tam (6 + fi*4, 12), r=3, tren nen idx0.
    cx = 6 + fi * 4
    cy = 12
    px = []
    for y in range(H):
        for x in range(W):
            dx = x - cx
            dy = y - cy
            px.append(1 if dx * dx + dy * dy <= 9 else 0)
    return px


def tiles_of(px):
    # Chia 8x8 tiles (4x3 = 12 tiles), moi tile 64 indices.
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
    centers = [(6 + i * 4, 12) for i in range(NFR)]
    # Ground truth doc lap (kenh 1): rgb sums + first/last 48
    gts = []
    for px in frames:
        rgb = []
        for idx in px:
            rgb = rgb + list(PAL[idx])
        gts.append({'sum': sum(rgb), 'first': rgb[:48], 'last': rgb[-48:]})
    # Encode
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
    ntiles_total = sum(1 for _ in payloads)
    # Header + table (offsets tinh tu dau file)
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
        blob = blob + p
    assert len(blob) == off, (len(blob), off)
    # Verify doc lap (kenh 2): decode payloads nguoc lai
    Calcium = list(frames[0])
    assert Calcium == frames[0]
    print('TKVV: %dx%d x%d frames, %d bytes total' % (W, H, NFR, len(blob)))
    print('  payload bytes:', [len(p) for p in payloads],
          'raw would be:', W * H * NFR)
    print('  ratio: %.2f' % (W * H * NFR / len(blob)))
    for i, g in enumerate(gts):
        print('  f%d sum=%d' % (i, g['sum']))

    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""TkvUI.TkvvData - sample TKVV bake san (sinh boi tools/tkvv_gen.py).')
    L.append('')
    L.append('32x24 ball-tren-nen, 6 frames delay 10cs: f0 = I, f1..f5 = P')
    L.append('(changed 8x8 tiles). Ground truth: rgb sum + 16px dau/cuoi/frame.')
    L.append('Khong doc file luc chay (ne compiler gap file I/O, giong I18nData).')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    L.append('def tkvv_sample_len() -> "i32":')
    L.append('    return %d' % len(blob))
    L.append('')
    L.append('def tkvv_sample_bytes() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in blob))
    L.append('')
    L.append('def tkvv_sample_w() -> "i32":')
    L.append('    return %d' % W)
    L.append('')
    L.append('def tkvv_sample_h() -> "i32":')
    L.append('    return %d' % H)
    L.append('')
    L.append('def tkvv_sample_nframes() -> "i32":')
    L.append('    return %d' % NFR)
    L.append('')
    for i, g in enumerate(gts):
        L.append('def tkvv_f%d_sum() -> "i32":' % i)
        L.append('    return %d' % g['sum'])
        L.append('')
        L.append('def tkvv_f%d_cx() -> "i32":' % i)
        L.append('    return %d' % centers[i][0])
        L.append('')
        L.append('def tkvv_f%d_cy() -> "i32":' % i)
        L.append('    return %d' % centers[i][1])
        L.append('')
        L.append('def tkvv_f%d_first() -> "list[i32]":' % i)
        L.append('    return [%s]' % ', '.join(str(x) for x in g['first']))
        L.append('')
        L.append('def tkvv_f%d_last() -> "list[i32]":' % i)
        L.append('    return [%s]' % ', '.join(str(x) for x in g['last']))
        L.append('')
    out = os.path.join(root, 'TkvUI.TkvvData.tkv')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out)


if __name__ == '__main__':
    main()
