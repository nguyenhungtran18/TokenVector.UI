#!/usr/bin/env bash
# tools/bench_all.ps1 - Benchmark driver 1 lệnh cho tất cả benchmark
# Chạy: bash tools/bench_all.sh

set -e

TKVC="/mnt/d/TokenVector/3.code/dist/tkvc.exe"
OUTDIR="build/bench"
mkdir -p "$OUTDIR"

echo "=== TkvUI Benchmark Suite ==="
echo "Build + run all benchmarks..."

# 1. Text render bench (std: 400 dong x 54 ky tu, 5 reps)
echo "[1/7] Text render bench..."
"$TKVC" build examples/TkvUI.BenchText.tkv --entry bench_text_block --out "$OUTDIR/bench_text.exe"
"$OUTDIR/bench_text.exe"

# 2. Widget creation + render bench (std: 1000 nut, construct x100 + render x20)
echo "[2/7] Widget creation bench..."
"$TKVC" build examples/TkvUI.BenchWidgets.tkv --entry bench_widgets_create --out "$OUTDIR/bench_widgets.exe"
"$OUTDIR/bench_widgets.exe"

# 3. CRUD bench (std: 10 reps x 1000 rows, fresh table/rep, in-memory)
echo "[3/7] CRUD bench..."
"$TKVC" build examples/TkvUI.CrudBench.tkv --entry bench_run --out "$OUTDIR/crudbench.exe"
"$OUTDIR/crudbench.exe"

# 3b. CRUD persist bench (P1: file-backed TKVSQL1 dual-slot)
echo "[3b/7] CRUD persist bench..."
"$TKVC" build examples/TkvUI.CrudBench.tkv --entry bench_persist --out "$OUTDIR/persistbench.exe"
"$OUTDIR/persistbench.exe"

# 4. PyQt6 baseline chuan hoa (cung workload, cung reps)
echo "[4/7] PyQt6 baseline..."
if command -v python3 >/dev/null 2>&1; then
    QT_QPA_PLATFORM=offscreen python3 tools/bench/bench_text_pyqt.py
    QT_QPA_PLATFORM=offscreen python3 tools/bench/bench_widgets_pyqt.py
    QT_QPA_PLATFORM=offscreen python3 tools/bench/crud_pyqt_bench_mem.py
else
    echo "SKIP: python3 not found"
fi

# 5. Memory bench (std: peak RSS cung workload text 108K chars)
echo "[5/7] Memory bench..."
if command -v python3 >/dev/null 2>&1; then
    python3 tools/bench/bench_mem.py "$OUTDIR/bench_text.exe"
    QT_QPA_PLATFORM=offscreen python3 tools/bench/bench_mem.py python3 tools/bench/bench_text_pyqt.py
else
    echo "SKIP: python3 not found"
fi

# 6. Live demo (khong phai bench so gang)
echo "[6/7] Live demo..."
"$TKVC" build examples/TkvUI.Live.tkv --entry run_live --out "$OUTDIR/live_mem.exe"
"$OUTDIR/live_mem.exe"

echo "=== Done ==="
echo "Kết quả ghi trong docs/BENCH.md (cập nhật thủ công sau khi chạy)"