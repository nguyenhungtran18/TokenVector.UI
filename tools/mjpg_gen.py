# -*- coding: utf-8 -*-
"""Bake 3 frame MJPEG baseline 160x120 + ground truth cho TkvUI.Mjpg.

Sample: gradient + o vuong trang di chuyen, PIL quality=50 (baseline,
4:2:0 interleaved, khong restart - assert cau truc). Ground truth doc lai
tu file (PIL decode): rgb sum + 16px dau/cuoi/frame (tolerance +-2 vi IDCT
float khac implement voi PIL, nhu moi decoder that khac nhau +-1).
Khong doc file luc chay (ne compiler gap file I/O).

  python3 tools/mjpg_gen.py  ->  writes TkvUI.MjpgData.tkv (UTF-8)
"""
import os
from PIL import Image

W = 160
H = 120
Q = 50


def make_frame(fi):
    im = Image.new('RGB', (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            px[x, y] = (x % 256, (y * 2) % 256, (x + y) % 256)
    sq = 20 + fi * 30
    for y in range(40, 70):
        for x in range(sq, sq + 30):
            px[x, y] = (255, 255, 255)
    return im


def assert_baseline(d):
    # SOI + SOF0 baseline + khong DRI/restart + SOS 3 comp
    assert d[:2] == b'\xff\xd8', d[:2].hex()
    assert b'\xff\xc0' in d, 'no SOF0'
    assert b'\xff\xc2' not in d, 'progressive!'
    assert b'\xff\xdd' not in d, 'DRI!'
    i = d.find(b'\xff\xc0')
    h = (d[i + 5] << 8) + d[i + 6]
    w = (d[i + 7] << 8) + d[i + 8]
    assert (w, h) == (W, H), (w, h)
    assert d[i + 9] == 3, 'comps'
    assert d[i + 11] == 0x22, 'want 4:2:0, got %02x' % d[i + 11]


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    datas = []
    gts = []
    for fi in range(3):
        path = os.path.join(root, 'build', 'mj_f%d.jpg' % fi)
        make_frame(fi).save(path, quality=Q)
        d = open(path, 'rb').read()
        assert_baseline(d)
        im = Image.open(path)
        raw = im.tobytes()
        assert len(raw) == W * H * 3
        gts.append({'sum': sum(raw), 'first': list(raw[:48]),
                    'last': list(raw[-48:])})
        datas.append(d)
        print('f%d: %d bytes, sum=%d' % (fi, len(d), sum(raw)))

    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""TkvUI.MjpgData - 3 frame MJPEG baseline 160x120 bake san.')
    L.append('')
    L.append('PIL quality=50 (SOF0 baseline, 4:2:0 interleaved, khong restart).')
    L.append('Ground truth: rgb sum + 16px dau/cuoi (tolerance +-2 - IDCT float).')
    L.append('Khong doc file luc chay (ne compiler gap file I/O).')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    zz = []
    for s in range(15):
        diag = [(x, s - x) for x in range(8) if 0 <= s - x < 8]
        if s % 2 == 1:
            diag = diag[::-1]
        zz = zz + [y * 8 + x for x, y in diag]
    assert len(zz) == 64 and len(set(zz)) == 64, 'zigzag'
    assert zz[:8] == [0, 1, 8, 16, 9, 2, 3, 10], zz[:8]
    L.append('def mjpg_zigzag() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in zz))
    L.append('')
    for fi, d in enumerate(datas):
        L.append('def mjpeg_f%d_len() -> "i32":' % fi)
        L.append('    return %d' % len(d))
        L.append('')
        L.append('def mjpeg_f%d_bytes() -> "list[i32]":' % fi)
        L.append('    return [%s]' % ', '.join(str(x) for x in d))
        L.append('')
        L.append('def mjpeg_f%d_sum() -> "i32":' % fi)
        L.append('    return %d' % gts[fi]['sum'])
        L.append('')
        L.append('def mjpeg_f%d_first() -> "list[i32]":' % fi)
        L.append('    return [%s]' % ', '.join(str(x) for x in gts[fi]['first']))
        L.append('')
        L.append('def mjpeg_f%d_last() -> "list[i32]":' % fi)
        L.append('    return [%s]' % ', '.join(str(x) for x in gts[fi]['last']))
        L.append('')
    out = os.path.join(root, 'TkvUI.MjpgData.tkv')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out)


if __name__ == '__main__':
    main()
