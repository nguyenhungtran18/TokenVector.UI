# -*- coding: utf-8 -*-
"""Craft MP4 2-track minimal + ground truth doc lap cho TkvUI.Mp4 (duong B).

boxes (big-endian, size gom 8 header): ftyp | moov{mvhd, trak{tkhd,
mdia{mdhd, hdlr, minf{vmhd/smhd, dinf, stbl{stsd, stts, stsc, stsz, stco}}}}}
| mdat. Track 1 = video avc1 (3 samples), track 2 = audio mp4a (2 samples).
stsd entries du chi tiet de demux that (avcC sps/pps, esds toi thieu).

  python3 tools/mp4_gen.py  ->  writes TkvUI.Mp4Data.tkv (UTF-8)
"""
import os
import struct


def box(tag, payload):
    return struct.pack('>I', 8 + len(payload)) + tag + payload


def u16(v):
    return struct.pack('>H', v)


def u32(v):
    return struct.pack('>I', v)


def fullbox(tag, verflags, payload):
    return box(tag, verflags + payload)


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # ---- samples (distinct patterns de verify extract) ----
    vsizes = [100, 120, 90]
    vsamples = [bytes([0x65, 0x10 + i]) + bytes([(i * 7 + k) % 256 for k in range(sz - 2)])
                for i, sz in zip((0, 1, 2), vsizes)]
    asamples = [bytes([0x21, 0x20 + i]) + bytes([(i * 13 + k) % 256 for k in range(sz - 2)])
                for i, sz in zip((0, 1), (50, 60))]
    assert [len(s) for s in vsamples] == vsizes
    assert [len(s) for s in asamples] == [50, 60]

    def avcc():
        sps = bytes([0x67, 0x42, 0xC0, 0x1E])
        pps = bytes([0x68, 0xCE])
        return box(b'avcC', bytes([1, 0x42, 0xC0, 0x1E, 0xFF, 0xE1])
                   + u16(len(sps)) + sps + bytes([1]) + u16(len(pps)) + pps)

    def avc1(w, h):
        e = bytes(6) + u16(1) + bytes(16) + u16(w) + u16(h)
        e = e + struct.pack('>I', 0x00480000) + struct.pack('>I', 0x00480000)
        e = e + struct.pack('>I', 0) + u16(1) + bytes([0]) * 32 + u16(24) + u16(0xFFFF)
        return box(b'avc1', e + avcc())

    def esds():
        inner = bytes([0x03, 0x19, 0x00, 0x01, 0x00, 0x04, 0x11, 0x40, 0x15,
                       0x00, 0x06, 0x00, 0x00, 0x01, 0xF4, 0x00, 0x05, 0x02,
                       0x12, 0x10, 0x06, 0x01, 0x02])
        return box(b'esds', bytes([0, 0, 0, 0]) + inner)

    def mp4a():
        e = bytes(6) + u16(1) + bytes(8) + u16(2) + u16(16) + struct.pack('>I', 44100 << 16)
        return box(b'mp4a', e + esds())

    def stbl(track):
        if track == 1:
            entries, w, h = avc1(160, 120), 160, 120
        else:
            entries, w, h = mp4a(), 0, 0
        stsd = fullbox(b'stsd', bytes(4), u32(1) + entries)
        if track == 1:
            stts = fullbox(b'stts', bytes(4), u32(1) + u32(3) + u32(1000))
            stsc = fullbox(b'stsc', bytes(4), u32(1) + u32(1) + u32(3) + u32(1))
            stsz = fullbox(b'stsz', bytes(4), u32(0) + u32(3) + b''.join(u32(x) for x in vsizes))
            stco = fullbox(b'stco', bytes(4), u32(1) + u32(0))
        else:
            stts = fullbox(b'stts', bytes(4), u32(1) + u32(2) + u32(1500))
            stsc = fullbox(b'stsc', bytes(4), u32(1) + u32(1) + u32(2) + u32(1))
            stsz = fullbox(b'stsz', bytes(4), u32(0) + u32(2) + u32(50) + u32(60))
            stco = fullbox(b'stco', bytes(4), u32(1) + u32(0))
        return box(b'stbl', stsd + stts + stsc + stsz + stco), stco

    def trak(tid, dur, hdlr, w, h, vol, isvideo):
        mdhd = fullbox(b'mdhd', bytes(4), u32(0) + u32(0) + u32(1000) + u32(dur) + u16(0x55C4) + u16(0))
        hdlr_b = fullbox(b'hdlr', bytes(4), u32(0) + hdlr + bytes(12) + (b'Video\0' if isvideo else b'Sound\0'))
        if isvideo:
            vmhd = fullbox(b'vmhd', bytes([0, 0, 0, 1]), u16(0) + u16(0) + u16(0) + u16(0))
        else:
            vmhd = fullbox(b'smhd', bytes(4), u16(0) + u16(0))
        dref = box(b'dref', bytes(4) + u32(1) + box(b'url ', bytes([0, 0, 0, 1])))
        dinf = box(b'dinf', dref)
        st, _ = stbl(tid)
        minf = box(b'minf', vmhd + dinf + st)
        mdia = box(b'mdia', mdhd + hdlr_b + minf)
        matrix = bytes(36)
        tkhd = fullbox(b'tkhd', bytes([0, 0, 0, 7]), u32(0) + u32(0) + u32(tid) + u32(0)
                       + u32(dur) + bytes(8) + u16(0) + u16(0) + vol + u16(0)
                       + matrix + struct.pack('>I', w << 16) + struct.pack('>I', h << 16))
        return box(b'trak', tkhd + mdia)

    mvhd = fullbox(b'mvhd', bytes(4), u32(0) + u32(0) + u32(1000) + u32(3000)
                   + struct.pack('>I', 0x10000) + u16(0x100) + u16(0) + bytes(10)
                   + bytes(36) + bytes(24) + u32(3))
    t1 = trak(1, 3000, b'vide', 160, 120, u16(0), True)
    t2 = trak(2, 3000, b'soun', 0, 0, u16(0x100), False)
    moov = box(b'moov', mvhd + t1 + t2)
    # stco patch: chunk offsets = len(ftyp)+len(moov)+8+running
    ftyp = box(b'ftyp', b'isom' + u32(512) + b'isomiso2')
    base = len(ftyp) + len(moov) + 8
    vchunk = base
    achunk = base + sum(vsizes)

    def patch_stco(trak_b, chunk_off):
        i = trak_b.find(b'stco')
        assert i > 0
        n = struct.unpack('>I', trak_b[i + 8:i + 12])[0]
        assert n == 1
        return trak_b[:i + 12] + u32(chunk_off) + trak_b[i + 16:]

    t1 = patch_stco(t1, vchunk)
    t2 = patch_stco(t2, achunk)
    moov = box(b'moov', mvhd + t1 + t2)
    mdat = box(b'mdat', b''.join(vsamples) + b''.join(asamples))
    blob = ftyp + moov + mdat
    print('mp4 bytes:', len(blob), 'moov:', len(moov))

    # ---- verify doc lap (kenh 2): walk + expected ----
    def boxes(buf, s, e):
        out = []
        o = s
        while o < e:
            sz = struct.unpack('>I', buf[o:o + 4])[0]
            assert sz >= 8, (o, sz)
            out.append((buf[o + 4:o + 8], o, sz))
            o = o + sz
        assert o == e
        return out

    top = boxes(blob, 0, len(blob))
    assert [t for t, _, _ in top] == [b'ftyp', b'moov', b'mdat'], top
    mo = [x for x in top if x[0] == b'moov'][0]
    moov_kids = boxes(blob, mo[1] + 8, mo[1] + mo[2])
    assert [t for t, _, _ in moov_kids] == [b'mvhd', b'trak', b'trak']
    exp = {'ntracks': 2, 'v_dur_ms': 3000, 'a_dur_ms': 3000,
           'v_nsamples': 3, 'a_nsamples': 2,
           'v_sizes': vsizes, 'a_sizes': [50, 60],
           'v_chunk': vchunk, 'a_chunk': achunk,
           'v_s0': list(vsamples[0][:8]), 'a_s1': list(asamples[1][:8]),
           'v_s2_off': vchunk + vsizes[0] + vsizes[1]}
    print('verify: 2 tracks, durations 3000/3000ms, samples 3/2')

    L = []
    L.append('# -*- coding: utf-8 -*-')
    L.append('"""TkvUI.Mp4Data - MP4 2-track craft san (sinh boi tools/mp4_gen.py).')
    L.append('')
    L.append('ftyp+moov(mvhd+2 trak avc1/mp4a)+mdat. Video 3 samples, audio 2.')
    L.append('Ground truth: tracks/durations/sizes/offsets/sample bytes.')
    L.append('Khong doc file luc chay.')
    L.append('"""')
    L.append('__tkv_import__ = ["TkvUI.Core"]')
    L.append('')
    L.append('def mp4_sample_len() -> "i32":')
    L.append('    return %d' % len(blob))
    L.append('')
    L.append('def mp4_sample_bytes() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in blob))
    L.append('')
    for k in ('ntracks', 'v_dur_ms', 'a_dur_ms', 'v_nsamples', 'a_nsamples',
              'v_chunk', 'a_chunk', 'v_s2_off'):
        L.append('def mp4_exp_%s() -> "i32":' % k)
        L.append('    return %d' % exp[k])
        L.append('')
    L.append('def mp4_exp_v_sizes() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in exp['v_sizes']))
    L.append('')
    L.append('def mp4_exp_a_sizes() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in exp['a_sizes']))
    L.append('')
    L.append('def mp4_exp_v_s0() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in exp['v_s0']))
    L.append('')
    L.append('def mp4_exp_a_s1() -> "list[i32]":')
    L.append('    return [%s]' % ', '.join(str(x) for x in exp['a_s1']))
    L.append('')
    out = os.path.join(root, 'TkvUI.Mp4Data.tkv')
    open(out, 'w', encoding='utf-8').write('\n'.join(L))
    print('wrote ' + out)


if __name__ == '__main__':
    main()
