"""Doi chung PyQt6 cho Phase 6.1: cua so trong idle 12s, in peak working set.

Chay:  python3 tools/bench/bench_mem_pyqt.py   (tu in ket qua, khong can driver)
"""
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "windows")

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer
import psutil

app = QApplication([])
w = QMainWindow()
w.setWindowTitle("bench-idle")
w.resize(400, 300)
w.show()

proc = psutil.Process()
peak = 0
t0 = time.perf_counter()
QTimer.singleShot(12000, app.quit)
while time.perf_counter() - t0 < 13:
    app.processEvents()
    try:
        rss = proc.memory_info().rss
        if rss > peak:
            peak = rss
    except Exception:
        pass
    time.sleep(0.2)

print(f"pyqt_peak_rss_kb={peak // 1024}")
