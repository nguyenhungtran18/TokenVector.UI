# -*- coding: utf-8 -*-
"""Bake sample GIF + ground truth cho TkvUI.Video (media decode thuần .tkv).

Chien luoc (rut ra sau 1 buoi debug LZW):
- KHONG hand-encode: chi encoder dat chuan moi duoc phep sinh bytes. O day
  dung PIL encoder (min code 8, interop chac chan), ground truth doc lai
  tu chinh file vua sinh. Kenh verify doc lap thu 2 se la .tkv decoder.
- Quy tac tang width LZW da phan xu bang thuc nghiem tren gradient 64x64
  (4096px, nhieu transition): early-change (nxt >= 2^W) decode dung
  4096/4096; late-change dung o 592. .tkv BAt BUOC dung early-change.

Sample 1 (unit): 8x8 2-frame (red/blue), delays 100/200ms.
Sample 2 (stress): 64x64 gradient RGB 1 frame (nhieu width transition).
Khong doc file luc chay (ne compiler gap file I/O, giong I18nData).

  python3 tools/gif_gen.py  ->  writes TkvUI.VideoGifData.tkv (UTF-8)
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def frame_truth(im, fi):
    im.seek(fi)
    delay = im.info.get('duration')
    px = list(im.convert('RGB').tobytes())
    n = im.size[0] * im.size[1]
    assert len(px) == n * 3, (len(px), n)
    s = sum(px)
    return {'delay': delay if delay is not None else 0,
            'sum': s, 'first': px[:48], 'last': px[-48:],
            'w': im.size[0], 'h': im.size[1], 'n': n}


def main():
    root = ROOT
    # --- sample 1 ---
    a = Image.new('RGB', (8, 8), (255, 0, 0))
    b = Image.new('RGB', (8, 8), (0, 0, 255))
    a.save(os.path.join(root, 'build', 'gif_s1.gif'),
           save_all=True, append_images=[b], duration=[100, 200], loop=0)
    # --- sample 2 ---
    g = Image.new('RGB', (64, 64))
    px = g.load()
    for y in range(64):
        for x in range(64):
            px[x, y] = ((x * 4) % 256, (y * 4) % 256, ((x + y) * 2) % 256)
    g.save(os.path.join(root, 'build', 'gif_s2.gif'), interlace=0)

    samples = []
    for name, path, nfs in (('s1', 'build/gif_s1.gif', 2),
                            ('s2', 'build/gif_s2.gif', 1)):
        full = os.path.join(root, path)
        data = open(full, 'rb').read()
        im = Image.open(full)
        assert im.n_frames == nfs, (name, im.n_frames)
        frames = [frame_truth(im, i) for i in range(nfs)]
        samples.append((name, data, frames))
        print('%s: %d bytes, %d frames' % (name, len(data), nfs))
        for i, f in enumerate(frames):
            print('  f%d %dx%d delay=%dms sum=%d' %
                  (i, f['w'], f['h'], f['delay'], f['sum']))

    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""TkvUI.VideoGifData - sample GIF bake san (sinh boi tools/gif_gen.py).')
    L.append('')
    L.append('Bytes do PIL encoder sinh (interop chac chan); ground truth (delay,')
    L.append('tong RGB, 16 pixel dau/cuoi moi frame) doc lai tu chinh file.')
    L.append('Khong doc file luc chay (ne compiler gap file I/O, giong I18nData).')
    L.append('')
    L.append('s1: 8x8 2-frame (delays 100/200ms). s2: 64x64 gradient 1 frame')
    L.append('(stress width transition LZW, quy tac early-change).')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    for name, data, frames in samples:
        L.append('def gif_%s_len() -> "i32":' % name)
        L.append('    return %d' % len(data))
        L.append('')
        L.append('def gif_%s_bytes() -> "list[i32]":' % name)
        L.append('    return [%s]' % ', '.join(str(x) for x in data))
        L.append('')
        L.append('def gif_%s_nframes() -> "i32":' % name)
        L.append('    return %d' % len(frames))
        L.append('')
        for i, f in enumerate(frames):
            L.append('def gif_%s_f%d_w() -> "i32":' % (name, i))
            L.append('    return %d' % f['w'])
            L.append('')
            L.append('def gif_%s_f%d_h() -> "i32":' % (name, i))
            L.append('    return %d' % f['h'])
            L.append('')
            L.append('def gif_%s_f%d_delay() -> "i32":' % (name, i))
            L.append('    return %d' % (f['delay'] // 10))
            L.append('')
            L.append('def gif_%s_f%d_sum() -> "i32":' % (name, i))
            L.append('    return %d' % f['sum'])
            L.append('')
            L.append('def gif_%s_f%d_first() -> "list[i32]":' % (name, i))
            L.append('    return [%s]' % ', '.join(str(x) for x in f['first']))
            L.append('')
            L.append('def gif_%s_f%d_last() -> "list[i32]":' % (name, i))
            L.append('    return [%s]' % ', '.join(str(x) for x in f['last']))
            L.append('')
    out = os.path.join(root, 'TkvUI.VideoGifData.tkv')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out)


if __name__ == '__main__':
    main()
