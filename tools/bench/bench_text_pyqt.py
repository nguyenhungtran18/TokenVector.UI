"""Doi chung PyQt6 cho Phase 6.2: render 400 dong x 54 ky tu len QImage (offscreen).

Chay:  QT_QPA_PLATFORM=offscreen python3 tools/bench/bench_text_pyqt.py
"""
import os
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtGui import QImage, QPainter, QFont, QColor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

LINE = "the quick brown fox jumps over the lazy dog 0123456789"
assert len(LINE) == 54, len(LINE)
NLINES = 400
STEP = 8
W, H = 340, 3200
REPS = 5

app = QApplication([])
font = QFont("Consolas")
font.setPixelSize(9)
img = QImage(W, H, QImage.Format.Format_ARGB32)

times = []
for _ in range(REPS):
    img.fill(QColor(0, 0, 0))
    p = QPainter(img)
    p.setFont(font)
    p.setPen(QColor(255, 255, 255))
    t0 = time.perf_counter()
    y = 0
    for _ in range(NLINES):
        p.drawText(0, y, LINE)
        y += STEP
    p.end()
    times.append((time.perf_counter() - t0) * 1000.0)

avg = sum(times) / len(times)
print(f"pyqt_ms_per_block={avg:.1f} reps={REPS} lines={NLINES} chars={NLINES * len(LINE)}")
print(f"runs={[f'{t:.1f}' for t in times]}")
