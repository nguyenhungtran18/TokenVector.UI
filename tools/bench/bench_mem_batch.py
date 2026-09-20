"""Do peak RSS hang loat exe (nghien cuu MEM): in KB file + peak RSS.
Chay:  python3 tools/bench/bench_mem_batch.py build/a.exe build/b.exe ...
"""
import subprocess
import sys
import time

import psutil

POLL = 0.005


def peak_of(cmd):
    p = subprocess.Popen(cmd)
    try:
        proc = psutil.Process(p.pid)
    except psutil.NoSuchProcess:
        p.wait()
        return 0
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
    finally:
        if p.poll() is None:
            p.kill()
        p.wait()
    return peak // 1024


def main(argv):
    import os
    for exe in argv[1:]:
        kb = os.path.getsize(exe) // 1024
        peak = peak_of([exe])
        print(f"{exe}: file_kb={kb} peak_rss_kb={peak}")


if __name__ == "__main__":
    main(sys.argv)
