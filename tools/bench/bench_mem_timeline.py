"""Ve timeline RSS (nghien cuu MEM): poll RSS + forward stdout co timestamp.
Chay:  python3 tools/bench/bench_mem_timeline.py build/text_test.exe [pattern]
Chi in cac dong stdout_match pattern (de giam noise) + RSS moi 100ms.
"""
import subprocess
import sys
import time

import psutil


def main(argv):
    if len(argv) < 2:
        print("usage: bench_mem_timeline.py <exe> [match]")
        return 2
    match = argv[2] if len(argv) > 2 else None
    p = subprocess.Popen(
        [argv[1]], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1)
    proc = psutil.Process(p.pid)
    peak = 0
    t0 = time.perf_counter()
    last_log = 0.0
    import threading
    lines = []

    def reader():
        for ln in p.stdout:
            lines.append((time.perf_counter() - t0, ln.rstrip()))

    th = threading.Thread(target=reader, daemon=True)
    th.start()
    while p.poll() is None:
        try:
            rss = proc.memory_info().rss // 1024
            if rss > peak:
                peak = rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            break
        now = time.perf_counter() - t0
        if now - last_log >= 0.5:
            print(f"t={now:5.1f}s rss={rss}kb peak={peak}kb", flush=True)
            last_log = now
        time.sleep(0.05)
    p.wait()
    th.join(timeout=2)
    print(f"FINAL peak_rss_kb={peak}")
    if match:
        print(f"--- lines matching {match!r} ---")
        for t, ln in lines:
            if match in ln:
                print(f"t={t:5.1f}s {ln}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
