#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M1 crash-safety: kill-9 matrix that cho TkvUI.SQLite dual-slot persist.

Chay writer (examples/TkvUI.SqlCrash.tkv) -> kill that (TerminateProcess =
kill -9, khong cleanup) o 2 thoi diem -> chay checker xac nhan phuc hoi.

Ma tran:
  - mid-save: kill sau khi thay "WRITING i" (delay ngau nhien 10-80ms).
    Phan loai quan sat: khong thay "WROTE i" + gen tien (=i) -> kill roi
    giua save nhung save van commit; gen giu -> mat 1 save dang ghi.
  - between: kill ngay khi thay "WROTE i" (writer dang spin giua 2 save).

Bat bien moi cycle: checker SQLCRASH_OK, gen khong giam, count == gen + PAD,
sum == count*(count+1)//2 (PAD = 2000, hardcode khop writer/checker).

Dung: python3 tools/sql_crashkill.py [--tkvc ...] [--mid 8] [--between 4]
Chi chay tren Windows (writer dung GetTickCount/kernel32).
"""
import argparse
import os
import random
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
DB_A = os.path.join(BUILD, "sqlcrash.db.a")
DB_B = os.path.join(BUILD, "sqlcrash.db.b")


def find_tkvc(cli):
    if cli and os.path.isfile(cli):
        return cli
    for cand in (r"D:\TokenVector\3.code\dist\tkvc.exe",
                 "/d/TokenVector/3.code/dist/tkvc.exe"):
        if os.path.isfile(cand):
            return cand
    raise SystemExit("khong tim thay tkvc.exe (truyen --tkvc)")


def build(tkvc, src, entry, exe):
    r = subprocess.run([tkvc, "build", src, "--entry", entry, "--out", exe],
                       cwd=ROOT, capture_output=True, text=True, timeout=300)
    if not os.path.isfile(exe):
        print("BUILD FAIL", entry)
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
        raise SystemExit(1)
    print("build ok:", os.path.basename(exe))


def run_checker(check_exe):
    r = subprocess.run([check_exe], cwd=ROOT, capture_output=True,
                       text=True, timeout=120)
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"CHECK gen=(\d+) count=(\d+) sum=(\d+)", out)
    ok = ("SQLCRASH_OK" in out) and (r.returncode == 0) and bool(m)
    gen = count = total = -1
    if m:
        gen, count, total = int(m.group(1)), int(m.group(2)), int(m.group(3))
        ok = ok and (count == gen + 2000) and (total == count * (count + 1) // 2)
    return ok, gen, count, total, out.strip().splitlines()[-3:]


def one_cycle(writer_exe, mode, rng):
    """Chay writer, kill theo mode, tra (bucket, writing_i, wrote_i)."""
    p = subprocess.Popen([writer_exe], cwd=ROOT, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    writing_i = 0
    wrote_i = 0
    killed = False
    t0 = time.time()
    try:
        for line in p.stdout:
            line = line.strip()
            m = re.match(r"WRITING (\d+)", line)
            if m:
                writing_i = int(m.group(1))
                if mode == "mid":
                    time.sleep(rng.uniform(0.01, 0.08))
                    p.kill()  # TerminateProcess: kill -9 that, khong cleanup
                    killed = True
                    break
                continue
            m = re.match(r"WROTE (\d+)", line)
            if m:
                wrote_i = int(m.group(1))
                if mode == "between":
                    p.kill()
                    killed = True
                    break
            if time.time() - t0 > 30:
                break
    finally:
        if not killed:
            try:
                p.kill()
            except Exception:
                pass
        try:
            rest = p.communicate(timeout=15)[0] or ""
        except Exception:
            rest = ""
        for line in rest.splitlines():
            m = re.match(r"WROTE (\d+)", line.strip())
            if m:
                wrote_i = max(wrote_i, int(m.group(1)))
    if writing_i == 0:
        return "NO_WRITING", writing_i, wrote_i
    if wrote_i >= writing_i:
        return "between", writing_i, wrote_i
    return "mid", writing_i, wrote_i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tkvc", default="")
    ap.add_argument("--mid", type=int, default=8)
    ap.add_argument("--between", type=int, default=4)
    ap.add_argument("--seed", type=int, default=20260922)
    args = ap.parse_args()
    if os.name != "nt":
        raise SystemExit("chi chay tren Windows (writer pinvoke kernel32)")

    tkvc = find_tkvc(args.tkvc)
    writer_exe = os.path.join(BUILD, "sqlcrash_writer.exe")
    check_exe = os.path.join(BUILD, "sqlcrash_check.exe")
    build(tkvc, "examples/TkvUI.SqlCrash.tkv", "sqlcrash_writer", writer_exe)
    build(tkvc, "examples/TkvUI.SqlCrash.tkv", "sqlcrash_check", check_exe)

    for f in (DB_A, DB_B):
        try:
            os.remove(f)
        except OSError:
            pass

    rng = random.Random(args.seed)
    modes = ["mid"] * args.mid + ["between"] * args.between
    rng.shuffle(modes)
    buckets = {"mid_uncommitted": 0, "mid_committed": 0, "between": 0}
    prev_gen = 0
    fails = []
    for n, mode in enumerate(modes, 1):
        bucket, wi, wo = one_cycle(writer_exe, mode, rng)
        ok, gen, count, total, tail = run_checker(check_exe)
        detail = "cycle %d/%d mode=%s -> bucket=%s WRITING=%d WROTE=%d CHECK gen=%d count=%d sum=%d" % (
            n, len(modes), mode, bucket, wi, wo, gen, count, total)
        print(detail)
        good = ok and gen >= prev_gen and gen >= 1
        if not good and prev_gen == 0 and "rc=2" in "|".join(tail):
            # Kill truoc save hoan tat DAU TIEN: chua co gi committed -> rc 2
            # la dung (giong SQLite: kill truoc commit dau -> DB rong).
            print("  (kill truoc commit dau tien -> DB rong, hop le)")
            buckets["mid_first_empty"] = buckets.get("mid_first_empty", 0) + 1
            good = True
        if not good:
            fails.append(detail + " TAIL=" + "|".join(tail))
        else:
            if bucket == "mid":
                buckets["mid_committed" if gen >= wi else "mid_uncommitted"] += 1
            elif bucket == "between":
                buckets["between"] += 1
            else:
                fails.append(detail + " (writer khong chay)")
        prev_gen = max(prev_gen, gen)
    print("buckets:", buckets)
    if fails:
        print("FAIL %d cycle:" % len(fails))
        for f in fails:
            print("  " + f)
        print("SQL_CRASHKILL_FAIL")
        return 1
    if buckets["mid_uncommitted"] == 0:
        print("CANH BAO: chua bat duoc kill that su giua save (toan bo commit hoac between)")
    print("SQL_CRASHKILL_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
