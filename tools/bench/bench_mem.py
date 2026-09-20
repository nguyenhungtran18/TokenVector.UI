"""Do peak RSS cua 1 lenh (chuan hoa MEM 2026-19): chay tien trinh con,
lay mau RSS moi 5ms cho den khi ket thuc, in peak KB + wall time.

Dung de so cong bang: cung workload text render 108K chars:
  python3 tools/bench/bench_mem.py build/bench_text.exe
  python3 tools/bench/bench_mem.py python3 tools/bench/bench_text_pyqt.py

Chay:  python3 tools/bench/bench_mem.py <cmd...>
Env QT_QPA_PLATFORM truyen tu moi truong hien tai (dat offscreen cho PyQt).
"""
import subprocess
import sys
import time

import psutil

POLL = 0.005


def main(argv):
    if len(argv) < 2:
        print("usage: bench_mem.py <cmd...>")
        return 2
    t0 = time.perf_counter()
    p = subprocess.Popen(argv[1:])
    proc = psutil.Process(p.pid)
    peak = 0
    try:
        while p.poll() is None:
            try:
                rss = proc.memory_info().rss
                if rss > peak:
                    peak = rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
            time.sleep(POLL)
        try:
            rss = proc.memory_info().rss
            if rss > peak:
                peak = rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    finally:
        if p.poll() is None:
            p.kill()
    dt = (time.perf_counter() - t0) * 1000.0
    print(f"peak_rss_kb={peak // 1024} wall_ms={dt:.0f} cmd={' '.join(argv[1:])}")
    return p.returncode or 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
