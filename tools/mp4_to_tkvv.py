#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chuot bach MP4 -> TKVV -> player (Chrome-canvas ingest, khong ffmpeg).

Chay: MP4 (URL hoac path) -> Chrome headless decode + chup N frames
(tools/chrome_cap.py, CDP screenshot) -> PNG -> TKVV blob + module .tkv
(tools/tkvv_import.py, decode-back EXACT) -> san sang play bang
examples/TkvUI.ClipPlayer.tkv (import module clip da sinh).

Dung:
  python3 tools/mp4_to_tkvv.py --mp4 <url|path> --out TkvUI.TkvvClipMp4.tkv \
      --prefix tkvm --n 8 --w 320 --h 240 --colors 16 --delay 10
In MP4_TO_TKVV_OK + tom tat (frames, blob bytes, ratio) khi xong.
"""
import argparse
import glob
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                       timeout=900)
    print(r.stdout[-1500:])
    if r.returncode != 0:
        print(r.stderr[-1500:])
        raise SystemExit('FAIL: ' + ' '.join(cmd[:3]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mp4', required=True)
    ap.add_argument('--out', default='TkvUI.TkvvClipMp4.tkv')
    ap.add_argument('--prefix', default='tkvm')
    ap.add_argument('--n', type=int, default=4)
    ap.add_argument('--w', type=int, default=320)
    ap.add_argument('--h', type=int, default=240)
    ap.add_argument('--colors', type=int, default=16)
    ap.add_argument('--delay', type=int, default=10)
    ap.add_argument('--frames-dir', default='build/ingest/fr')
    ap.add_argument('--port', type=int, default=9222)
    ap.add_argument('--chrome', default='')
    a = ap.parse_args()
    assert a.w % 8 == 0 and a.h % 8 == 0, 'w,h phai chia het cho 8 (TKVV tile)'

    mp4 = a.mp4
    if '://' in mp4:
        local = os.path.join(ROOT, 'build', 'ingest',
                             os.path.basename(mp4.split('?')[0]) or 'in.mp4')
        os.makedirs(os.path.dirname(local), exist_ok=True)
        print('download ' + mp4)
        urllib.request.urlretrieve(mp4, local)
        mp4 = os.path.relpath(local, ROOT)
    if not os.path.isfile(os.path.join(ROOT, mp4)):
        raise SystemExit('khong thay MP4: ' + mp4)

    for f in glob.glob(os.path.join(ROOT, a.frames_dir, 'frame_*.png')):
        os.remove(f)
    cap = [sys.executable, 'tools/chrome_cap.py', '--mp4', mp4,
           '--outdir', a.frames_dir, '--n', str(a.n), '--w', str(a.w),
           '--h', str(a.h), '--port', str(a.port)]
    if a.chrome:
        cap += ['--chrome', a.chrome]
    run(cap)
    imp = [sys.executable, 'tools/tkvv_import.py', '--frames',
           a.frames_dir + '/frame_*.png', '--out', a.out,
           '--prefix', a.prefix, '--colors', str(a.colors),
           '--delay', str(a.delay)]
    run(imp)
    print('MP4_TO_TKVV_OK src=%s clip=%s' % (mp4, a.out))
    print('play: tkvc.exe build examples/TkvUI.ClipPlayer.tkv '
          '--entry clipplayer_run --out build/clipplayer.exe')
    return 0


if __name__ == '__main__':
    sys.exit(main())
