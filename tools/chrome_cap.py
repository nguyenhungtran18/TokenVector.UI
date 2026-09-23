#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chup N frames tu file MP4 bang Chrome headless + CDP (stdlib only).

Khong dung canvas/events (seeked khong fire duoi headless/dump-dom):
navigate trang video -> dat currentTime qua Runtime.evaluate -> POLL
seeking/currentTime -> Page.captureScreenshot (PNG base64) -> luu file.

Dung: python3 tools/chrome_cap.py --mp4 build/ingest/sample.mp4 --outdir
  build/ingest/fr --n 8 --w 320 --h 240 [--port 9222] [--chrome ...]
Tra 0 + in CAPTURE_OK khi du N PNG doc duoc bang PIL.
"""
import argparse
import base64
import json
import os
import socket
import ssl
import subprocess
import sys
import time
import urllib.request
from hashlib import sha1

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGE = ('<!DOCTYPE html><html><head><meta charset="utf-8"><title>cap</title>'
        '<style>html,body{margin:0;padding:0;background:#000}'
        'video{width:%dpx;height:%dpx;display:block;object-fit:fill}</style></head><body>'
        '<video id="v" muted playsinline preload="auto" src="%s"></video>'
        '</body></html>')


class WS:
    def __init__(self, host, port, path):
        self.s = socket.create_connection((host, port), timeout=20)
        key = base64.b64encode(os.urandom(16)).decode()
        req = ('GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\n'
               'Connection: Upgrade\r\nSec-WebSocket-Key: %s\r\n'
               'Sec-WebSocket-Version: 13\r\n\r\n') % (path, host, port, key)
        self.s.sendall(req.encode())
        head = b''
        while b'\r\n\r\n' not in head:
            head = head + self.s.recv(4096)
        if b' 101 ' not in head.split(b'\r\n')[0]:
            raise RuntimeError('ws upgrade fail: ' + head[:80].decode('latin1'))
        self.buf = b''

    def _fill(self, n):
        while len(self.buf) < n:
            chunk = self.s.recv(65536)
            if not chunk:
                raise RuntimeError('ws closed')
            self.buf = self.buf + chunk

    def _frame(self):
        self._fill(2)
        b1, b2 = self.buf[0], self.buf[1]
        fin, op = (b1 & 0x80) != 0, b1 & 0x0F
        ln = b2 & 0x7F
        off = 2
        if ln == 126:
            self._fill(4)
            ln = int.from_bytes(self.buf[2:4], 'big')
            off = 4
        elif ln == 127:
            self._fill(10)
            ln = int.from_bytes(self.buf[2:10], 'big')
            off = 10
        if b2 & 0x80:
            self._fill(off + 4)
            mask = self.buf[off:off + 4]
            off = off + 4
        else:
            mask = None
        self._fill(off + ln)
        pay = self.buf[off:off + ln]
        self.buf = self.buf[off + ln:]
        if mask:
            pay = bytes(c ^ mask[i % 4] for i, c in enumerate(pay))
        return fin, op, pay

    def recv_msg(self, timeout=60):
        t0 = time.time()
        parts = []
        self.s.settimeout(5)
        while True:
            if time.time() - t0 > timeout:
                raise RuntimeError('ws recv timeout')
            try:
                fin, op, pay = self._frame()
            except socket.timeout:
                continue
            if op == 0x8:
                raise RuntimeError('ws close frame')
            if op == 0x9:
                self.send_raw(0xA, pay)
                continue
            if op in (0x1, 0x0):
                parts.append(pay)
            if fin:
                break
        return b''.join(parts).decode('utf-8')

    def send_raw(self, op, pay):
        if isinstance(pay, str):
            pay = pay.encode('utf-8')
        h = bytes([0x80 | op])
        ln = len(pay)
        if ln < 126:
            h = h + bytes([0x80 | ln])
        elif ln < 65536:
            h = h + bytes([0x80 | 126]) + ln.to_bytes(2, 'big')
        else:
            h = h + bytes([0x80 | 127]) + ln.to_bytes(8, 'big')
        mask = os.urandom(4)
        mp = bytes(c ^ mask[i % 4] for i, c in enumerate(pay))
        self.s.sendall(h + mask + mp)

    def close(self):
        try:
            self.send_raw(0x8, b'')
            self.s.close()
        except Exception:
            pass


class CDP:
    def __init__(self, ws):
        self.ws = ws
        self.seq = 0
        self.pending = {}

    def call(self, method, params=None, timeout=60):
        self.seq += 1
        if self.seq in self.pending:
            r = self.pending.pop(self.seq)
            if 'error' in r:
                raise RuntimeError('%s: %s' % (method, r['error']))
            return r.get('result', {})
        msg = json.dumps({'id': self.seq, 'method': method,
                          'params': params or {}})
        self.ws.send_raw(0x1, msg)
        while True:
            r = json.loads(self.ws.recv_msg(timeout))
            rid = r.get('id')
            if rid is None:
                continue
            if rid != self.seq:
                self.pending[rid] = r
                continue
            if 'error' in r:
                raise RuntimeError('%s: %s' % (method, r['error']))
            return r.get('result', {})

    def ev(self, expr, timeout=30):
        r = self.call('Runtime.evaluate',
                      {'expression': expr, 'returnByValue': True}, timeout)
        remote = r.get('result', {})
        return remote.get('value')


def find_chrome(cli):
    if cli and os.path.isfile(cli):
        return cli
    for c in (r'C:\Program Files\Google\Chrome\Application\chrome.exe',
              r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'):
        if os.path.isfile(c):
            return c
    raise SystemExit('khong thay chrome.exe (truyen --chrome)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mp4', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--n', type=int, default=8)
    ap.add_argument('--w', type=int, default=320)
    ap.add_argument('--h', type=int, default=240)
    ap.add_argument('--port', type=int, default=9222)
    ap.add_argument('--chrome', default='')
    a = ap.parse_args()
    mp4 = a.mp4 if os.path.isabs(a.mp4) else os.path.join(ROOT, a.mp4)
    outdir = a.outdir if os.path.isabs(a.outdir) else os.path.join(ROOT, a.outdir)
    os.makedirs(outdir, exist_ok=True)
    page = os.path.join(outdir, 'cap_page.html')
    # file:// URL: dung ten file goc de tranh copy video lon
    rel = os.path.relpath(mp4, outdir).replace('\\', '/')
    open(page, 'w', encoding='utf-8').write(PAGE % (a.w, a.h, rel))
    chrome = find_chrome(a.chrome)
    proc = subprocess.Popen(
        [chrome, '--headless=new', '--disable-gpu',
         '--allow-file-access-from-files',
         '--remote-debugging-port=%d' % a.port,
         '--window-size=%d,%d' % (a.w, a.h), 'about:blank'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        # doi DevTools san sang
        tabs = None
        for _ in range(100):
            time.sleep(0.2)
            try:
                with urllib.request.urlopen(
                        'http://127.0.0.1:%d/json/list' % a.port,
                        timeout=5) as r:
                    tabs = json.loads(r.read().decode('utf-8'))
                break
            except Exception:
                pass
        if not tabs:
            raise RuntimeError('devtools khong len')
        pages = [t for t in tabs if t.get('type') == 'page']
        if not pages:
            raise RuntimeError('khong thay page target: %s' %
                               [t.get('url') for t in tabs])
        wsurl = pages[0]['webSocketDebuggerUrl']
        host, port, path = '127.0.0.1', a.port, wsurl.split(':%d' % a.port)[1]
        cdp = CDP(WS(host, port, path))
        cdp.call('Page.enable')
        cdp.call('Emulation.setDeviceMetricsOverride',
                 {'width': a.w, 'height': a.h, 'deviceScaleFactor': 1,
                  'mobile': False})
        cdp.call('Page.navigate',
                 {'url': 'file:///' + page.replace('\\', '/')})
        # doi video co data
        dur = 0
        for _ in range(150):
            time.sleep(0.2)
            try:
                st = cdp.ev('[document.getElementById("v").readyState,'
                            'document.getElementById("v").duration||0].join("|")')
                rs, dur = st.split('|')
                if int(rs) >= 2 and float(dur) > 0:
                    dur = float(dur)
                    break
            except Exception:
                pass
        if not dur:
            raise RuntimeError('video khong load (readyState/duration)')
        print('video dur=%.3f' % dur)
        got = 0
        for i in range(a.n):
            t = (dur / a.n) * i + 0.01
            cdp.ev('document.getElementById("v").currentTime=%f' % t)
            ok = False
            for _ in range(50):
                time.sleep(0.2)
                st = cdp.ev('[document.getElementById("v").seeking,'
                            'document.getElementById("v").currentTime].join("|")')
                sk, ct = st.split('|')
                if sk == 'false' and abs(float(ct) - t) < 0.35:
                    ok = True
                    break
            if not ok:
                raise RuntimeError('seek stall frame %d' % i)
            time.sleep(0.3)
            img = cdp.call('Page.captureScreenshot', {'format': 'png'},
                           timeout=30)['data']
            fn = os.path.join(outdir, 'frame_%03d.png' % i)
            open(fn, 'wb').write(base64.b64decode(img))
            got += 1
            print('frame %d t=%.2f' % (i, t))
        print('CAPTURE_OK %d/%d' % (got, a.n))
        return 0
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=10)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass


if __name__ == '__main__':
    sys.exit(main())
