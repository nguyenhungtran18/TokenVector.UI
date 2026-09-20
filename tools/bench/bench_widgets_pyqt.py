"""Doi chung PyQt6 cho Phase 6.3 (chuan hoa 2026-09-19).

Workload giong he TKV `examples/TkvUI.BenchWidgets.tkv`:
  - construct: 1000 QPushButton("B") trong QGridLayout 10 cot, x100 reps
  - paint: render 1 layout 1000 nut len QImage 820x2600 offscreen, x5 reps

Chay:  QT_QPA_PLATFORM=offscreen python3 tools/bench/bench_widgets_pyqt.py
"""
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout
from PyQt6.QtGui import QImage

N = 1000
REPS_CONSTRUCT = 100
REPS_PAINT = 5
W, H = 820, 2600

app = QApplication([])


def build_grid():
    w = QWidget()
    lay = QGridLayout(w)
    lay.setSpacing(2)
    for i in range(N):
        b = QPushButton("B")
        lay.addWidget(b, i // 10, i % 10)
    return w


# construct x100
ctimes = []
for _ in range(REPS_CONSTRUCT):
    t0 = time.perf_counter()
    w = build_grid()
    dt = (time.perf_counter() - t0) * 1000.0
    ctimes.append(dt)
    w.deleteLater()
cavg = sum(ctimes) / len(ctimes)

# paint x5 (1 layout dung lai, render ra QImage offscreen)
w = build_grid()
w.resize(W, H)
img = QImage(W, H, QImage.Format.Format_ARGB32)
ptimes = []
for _ in range(REPS_PAINT):
    img.fill(0xFF000000)
    t0 = time.perf_counter()
    w.render(img)
    ptimes.append((time.perf_counter() - t0) * 1000.0)
pavg = sum(ptimes) / len(ptimes)
w.deleteLater()

print(f"pyqt_construct_ms_per_1000={cavg:.2f} reps={REPS_CONSTRUCT} n={N}")
print(f"pyqt_paint_ms_per_1000={pavg:.1f} reps={REPS_PAINT} n={N}")
print(f"pyqt_construct_runs={[f'{t:.1f}' for t in ctimes[:5]]}...")
print(f"pyqt_paint_runs={[f'{t:.1f}' for t in ptimes]}")
