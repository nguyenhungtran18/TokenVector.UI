# -*- coding: utf-8 -*-
"""P3-B3: chuan chong-flake cho benchmark (nguong + repeat + percentile).

Van de: timer TKV = GetTickCount (quantum ~16ms) lam so nhay +-16..32ms
giua cac lan chay; ket luan thang/thua phai dung tren lap lai, khong
copy 1 so don.

Dung:
  python3 tools/bench_stats.py --repeat 3 --metric text_atlas \\
      --pattern 'atlas_ms=(\\d+)' --unit ms --lt 100 --tol-abs 32 -- build/bench/bench_text.exe
  python3 tools/bench_stats.py --selftest   # kiem tra toan percentile (10 check)

Thoat 0 + `BENCH_OK` neu dat nguong VA on dinh; nguoc lai `BENCH_FAIL` + exit 1.
"""
import re
import subprocess
import sys


def pct(sorted_vals, p):
    # Percentile noi suy tuyen tinh, p trong [0, 100]. Can it nhat 1 mau.
    n = len(sorted_vals)
    if n == 0:
        return 0.0
    if n == 1:
        return float(sorted_vals[0])
    if p <= 0:
        return float(sorted_vals[0])
    if p >= 100:
        return float(sorted_vals[-1])
    rank = p / 100.0 * (n - 1)
    lo = int(rank)
    hi = lo + 1
    frac = rank - lo
    return float(sorted_vals[lo]) + frac * (float(sorted_vals[hi]) - float(sorted_vals[lo]))


def evaluate(vals, tol_abs, tol_rel):
    # Tra dict min/med/max/spread/stable. stable khi spread <= max(tol_abs, tol_rel*med).
    s = sorted(vals)
    mn = float(s[0])
    med = pct(s, 50)
    mx = float(s[-1])
    spread = mx - mn
    allow = tol_abs
    rel_allow = tol_rel * med
    if rel_allow > allow:
        allow = rel_allow
    return {'n': len(s), 'min': mn, 'med': med, 'max': mx,
            'spread': spread, 'allow': allow, 'stable': 1 if spread <= allow else 0}


def extract(output, pattern):
    m = re.search(pattern, output)
    if not m:
        return None
    return float(m.group(1))


def run_once(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def selftest():
    bad = 0
    cases = [
        ('p50 odd', pct([10, 20, 30], 50), 20.0),
        ('p50 even', pct([10, 20, 30, 40], 50), 25.0),
        ('p0', pct([10, 20, 30], 0), 10.0),
        ('p100', pct([10, 20, 30], 100), 30.0),
        ('p25', pct([0, 100], 25), 25.0),
        ('single', pct([7], 50), 7.0),
    ]
    for name, got, want in cases:
        ok = abs(got - want) < 1e-9
        print(('  PASS ' if ok else '  FAIL ') + name + ' = ' + str(got))
        if not ok:
            bad = bad + 1
    e = evaluate([44, 47, 47], 32.0, 0.2)
    ok = e['med'] == 47.0 and e['stable'] == 1 and e['spread'] == 3.0
    print(('  PASS ' if ok else '  FAIL ') + 'stable small spread')
    if not ok:
        bad = bad + 1
    e2 = evaluate([0, 100, 200], 32.0, 0.2)
    ok2 = e2['stable'] == 0 and e2['med'] == 100.0
    print(('  PASS ' if ok2 else '  FAIL ') + 'flaky detected')
    if not ok2:
        bad = bad + 1
    v = extract('atlas_ms=47 classic_ms=391 lines=5', r'atlas_ms=(\d+)')
    ok3 = v == 47.0
    print(('  PASS ' if ok3 else '  FAIL ') + 'extract')
    if not ok3:
        bad = bad + 1
    v2 = extract('no numbers here', r'atlas_ms=(\d+)')
    ok4 = v2 is None
    print(('  PASS ' if ok4 else '  FAIL ') + 'extract miss')
    if not ok4:
        bad = bad + 1
    print('benchstats: ' + str(10 - bad) + '/10')
    if bad == 0:
        print('BENCHSTATS_OK')
        return 0
    print('BENCHSTATS_FAIL')
    return 1


def main(argv):
    if '--selftest' in argv:
        return selftest()
    import argparse
    ap = argparse.ArgumentParser(description='P3-B3 bench stability gate')
    ap.add_argument('--repeat', type=int, default=3)
    ap.add_argument('--metric', required=True)
    ap.add_argument('--pattern', required=True)
    ap.add_argument('--unit', default='ms')
    ap.add_argument('--lt', type=float, default=None)
    ap.add_argument('--gt', type=float, default=None)
    ap.add_argument('--tol-abs', type=float, default=32.0)
    ap.add_argument('--tol-rel', type=float, default=0.2)
    ap.add_argument('cmd', nargs='+')
    a = ap.parse_args(argv)
    vals = []
    for i in range(a.repeat):
        rc, out = run_once(a.cmd)
        if rc != 0:
            print('FAIL  ' + a.metric + ' run %d exit %d' % (i + 1, rc))
            print('BENCH_FAIL ' + a.metric + ' (exit)')
            return 1
        v = extract(out, a.pattern)
        if v is None:
            print('FAIL  ' + a.metric + ' run %d thieu so (pattern %s)' % (i + 1, a.pattern))
            print('BENCH_FAIL ' + a.metric + ' (parse)')
            return 1
        vals.append(v)
        print('  rep %d: %s=%g%s' % (i + 1, a.metric, v, a.unit))
    e = evaluate(vals, a.tol_abs, a.tol_rel)
    ok = e['stable'] == 1
    reason = 'stable' if ok else 'FLAKY spread=%g>allow=%g' % (e['spread'], e['allow'])
    if a.lt is not None:
        if not e['med'] < a.lt:
            ok = False
            reason = reason + '; med=%g>=%g' % (e['med'], a.lt)
    if a.gt is not None:
        if not e['med'] > a.gt:
            ok = False
            reason = reason + '; med=%g<=%g' % (e['med'], a.gt)
    print('%s %s n=%d min=%g med=%g max=%g%s (%s)'
          % ('PASS ' if ok else 'FAIL ', a.metric, e['n'], e['min'],
             e['med'], e['max'], a.unit, reason))
    print(('BENCH_OK ' if ok else 'BENCH_FAIL ') + a.metric)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
