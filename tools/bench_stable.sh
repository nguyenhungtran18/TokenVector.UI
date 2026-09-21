#!/usr/bin/env bash
# P3-B3: bench stability gate - moi bench chay 3 lan, danh gia percentile +
# nguong qua tools/bench_stats.py (chong flake GetTickCount quantum ~16ms).
#   bash tools/bench_stable.sh
# Nguong lay tu docs/BENCH.md (do 2026-09-20) + headroom chong false alarm:
#   text atlas tong 5 block ~47ms -> <100; widgets render ~593ms/20 -> <900;
#   crud TOTAL ~8ms/rep -> <20.

set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TKVC="${TKVC:-/d/TokenVector/3.code/dist/tkvc.exe}"
if [ ! -x "$TKVC" ]; then
  TKVC="$(command -v tkvc.exe 2>/dev/null || command -v tkvc 2>/dev/null || true)"
fi
if [ -z "$TKVC" ] || [ ! -x "$TKVC" ]; then
  echo "Khong tim thay tkvc.exe. Dat TKVC=/duong/dan/tkvc.exe" >&2
  exit 2
fi

OUTDIR="${OUT:-build/bench}"
mkdir -p "$OUTDIR"

echo "=== build benches (1 lan) ==="
"$TKVC" build examples/TkvUI.BenchText.tkv --entry bench_text_block --out "$OUTDIR/bench_text.exe"
"$TKVC" build examples/TkvUI.BenchWidgets.tkv --entry bench_widgets_create --out "$OUTDIR/bench_widgets.exe"
"$TKVC" build examples/TkvUI.CrudBench.tkv --entry bench_run --out "$OUTDIR/crudbench.exe"

echo "=== stability gates (3 lan/bench) ==="
FAIL=0
python3 tools/bench_stats.py --repeat 3 --metric text_atlas \
  --pattern 'atlas_ms=(\d+)' --unit ms --lt 100 --tol-abs 32 -- "$OUTDIR/bench_text.exe" || FAIL=1
python3 tools/bench_stats.py --repeat 3 --metric widgets_render \
  --pattern 'render_ms=(\d+)' --unit ms --lt 900 --tol-abs 64 -- "$OUTDIR/bench_widgets.exe" || FAIL=1
python3 tools/bench_stats.py --repeat 3 --metric crud_total \
  --pattern 'TOTAL avg/rep: (\d+)ms' --unit ms --lt 20 --tol-abs 16 -- "$OUTDIR/crudbench.exe" || FAIL=1

if [ $FAIL -ne 0 ]; then
  echo "BENCH_STABLE_FAIL"
  exit 1
fi
echo "BENCH_STABLE_OK"
