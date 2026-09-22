# -*- coding: utf-8 -*-
"""Ingest tong quat: PNG-sequence bat ky -> TKVV (custom format, giong TKVA).

Khac tkvv_gen/tkvv_play_gen (content tong hop code tay): doc PNG that,
quantize ve palette chung (PIL adaptive tren frame dau, dither NONE de
deterministic), tile-diff I/P, verify doc nguoc doc lap (decode-back so
voi input, exact), xuat module .tkv bake + file .tkvv doc lap.

  python3 tools/tkvv_import.py --frames "build/play_f*.png" --out TkvUI.TkvvClip.tkv --prefix tkvvc --colors 8 --delay 10
"""
import argparse
import glob
import os
from PIL import Image

T = 8


def u16(v):
    return bytes([v & 0xFF, (v >> 8) & 0xFF])


def u32(v):
    return bytes([v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF])


def tiles_of(px, w, h):
    out = []
    for ty in range(h // T):
        for tx in range(w // T):
            t = []
            for y in range(T):
                for x in range(T):
                    t.append(px[(ty * T + y) * w + tx * T + x])
            out.append(t)
    return out


def decode_back(blob, w, h, nfr):
    # Kênh verify doc lap: parse + reconstruct (I copy, P apply).
    assert blob[:4] == b'TKVV'
    palsz = int.from_bytes(blob[12:14], 'little')
    pal = [tuple(blob[14 + i * 3:17 + i * 3]) for i in range(palsz)]
    delays = [int.from_bytes(blob[14 + palsz * 3 + i * 2:16 + palsz * 3 + i * 2], 'little')
              for i in range(nfr)]
    toff = 14 + palsz * 3 + nfr * 2
    frames = []
    prev = None
    for fi in range(nfr):
        t = blob[toff]
        o = int.from_bytes(blob[toff + 1:toff + 5], 'little')
        ln = int.from_bytes(blob[toff + 5:toff + 9], 'little')
        toff = toff + 9
        pay = blob[o:o + ln]
        if t == 0:
            px = []
            for ty in range(h // T):
                for yy in range(T):
                    for tx in range(w // T):
                        base = ((ty * (w // T) + tx) * 64) + yy * T
                        px = px + list(pay[base:base + T])
            # ^ tile-order -> raster (de interleave dung nhu decoder that)
            assert len(px) == w * h
        else:
            assert prev is not None
            px = list(prev)
            nt = int.from_bytes(pay[0:2], 'little')
            p = 2
            for _ in range(nt):
                ti = int.from_bytes(pay[p:p + 2], 'little')
                p = p + 2
                tx, ty = ti % (w // T), ti // (w // T)
                for yy in range(T):
                    for xx in range(T):
                        px[(ty * T + yy) * w + tx * T + xx] = pay[p]
                        p = p + 1
        frames.append((px, delays[fi]))
        prev = px
    return pal, frames


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--frames', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--prefix', required=True)
    ap.add_argument('--colors', type=int, default=16)
    ap.add_argument('--delay', type=int, default=10)
    a = ap.parse_args()
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    paths = sorted(glob.glob(os.path.join(root, a.frames)))
    assert len(paths) >= 1, 'khong thay PNG: ' + a.frames
    assert a.colors <= 256
    # Shared palette tu frame dau (deterministic, khong dither)
    first = Image.open(paths[0]).convert('RGB')
    w, h = first.size
    assert w % 8 == 0 and h % 8 == 0, (w, h)
    palimg = first.quantize(colors=a.colors, dither=Image.NONE)
    praw = palimg.getpalette()
    palrgb = []
    for i in range(a.colors):
        cell = list(praw[i * 3:i * 3 + 3]) + [0, 0, 0]
        palrgb.append((cell[0], cell[1], cell[2]))
    assert len(palrgb) == a.colors
    frames = []
    for p in paths:
        im = Image.open(p).convert('RGB')
        assert im.size == (w, h), (p, im.size)
        q = im.quantize(palette=palimg, dither=Image.NONE)
        frames.append(list(q.tobytes()))
    nfr = len(frames)
    # Encode I/P
    payloads = []
    ftypes = []
    prev_tiles = None
    for fi, px in enumerate(frames):
        tiles = tiles_of(px, w, h)
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
    head_len = 4 + 2 * 5 + len(palrgb) * 3 + nfr * 2 + nfr * 9
    off = head_len
    table = bytearray()
    for fi in range(nfr):
        table = table + bytes([ftypes[fi]]) + u32(off) + u32(len(payloads[fi]))
        off = off + len(payloads[fi])
    blob = (b'TKVV' + u16(1) + u16(w) + u16(h) + u16(nfr) + u16(len(palrgb)))
    for c in palrgb:
        blob = blob + bytes(c)
    for _ in range(nfr):
        blob = blob + u16(a.delay)
    blob = blob + bytes(table)
    for p in payloads:
        blob = blob + bytes(p)
    assert len(blob) == off, (len(blob), off)
    # File .tkvv doc lap (artifact interchange, kem player tuong lai doc truc tiep)
    tvp = os.path.join(root, os.path.splitext(a.out)[0] + '.tkvv')
    open(tvp, 'wb').write(blob)
    # Verify doc lap: decode-back vs input (exact - lossless o muc index)
    pal2, back = decode_back(blob, w, h, nfr)
    assert [tuple(x) for x in pal2] == [tuple(x) for x in palrgb], 'palette'
    assert len(back) == nfr
    for i, ((px, dl), src) in enumerate(zip(back, frames)):
        assert px == src, 'frame %d mismatch' % i
        assert dl == a.delay, (i, dl)
    print('TKVV-IMPORT: %d PNG %dx%d -> %d bytes (raw %d, ratio %.2f), decode-back EXACT %d/%d frames' %
          (nfr, w, h, len(blob), w * h * nfr, w * h * nfr / len(blob), nfr, nfr))
    # Bake module .tkv
    pre = a.prefix
    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""%s - clip ingest tu PNG-sequence (sinh boi tools/tkvv_import.py).' % os.path.basename(a.out))
    L.append('')
    L.append('%d frames %dx%d, palette %d mau, delays %dcs. Ground truth: index-exact.' % (nfr, w, h, len(palrgb), a.delay))
    L.append('Khong doc file luc chay.')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    L.append('def %s_len() -> "i32":' % pre)
    L.append('    return %d' % len(blob))
    L.append('')
    L.append('def %s_bytes() -> "list[i32]":' % pre)
    L.append('    return [%s]' % ', '.join(str(x) for x in blob))
    L.append('')
    L.append('def %s_nframes() -> "i32":' % pre)
    L.append('    return %d' % nfr)
    L.append('')
    # Ground truth RGB sum/frame (khop tkvv_render_rgb + sum trong .tkv)
    for i, ((px, dl), src) in enumerate(zip(back, frames)):
        s = 0
        for idx in px:
            c = palrgb[idx]
            s = s + c[0] + c[1] + c[2]
        L.append('def %s_f%d_sum() -> "i32":' % (pre, i))
        L.append('    return %d' % s)
        L.append('')
        print('  f%d rgbsum=%d' % (i, s))
    out = os.path.join(root, a.out)
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out + ' + ' + tvp)


if __name__ == '__main__':
    main()
