#!/usr/bin/env bash
# TkvUI verify: build + chay TOAN BO selftest headless bang tkvc.
# Thoat != 0 neu co muc FAIL. Cac demo mo cua so that (TkvUI.Demo, run_live) phai chay tay.
#
#   bash tools/verify.sh
#   TKVC=/d/TokenVector/3.code/dist/tkvc.exe bash tools/verify.sh
#   OUT=build/verify bash tools/verify.sh

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TKVC="${TKVC:-/d/TokenVector/3.code/dist/tkvc.exe}"
if [ ! -x "$TKVC" ]; then
  TKVC="$(command -v tkvc.exe 2>/dev/null || command -v tkvc 2>/dev/null || true)"
fi
if [ -z "$TKVC" ] || [ ! -x "$TKVC" ]; then
  echo "Khong tim thay tkvc.exe. Dat bien moi truong TKVC=/duong/dan/tkvc.exe" >&2
  exit 2
fi
echo "tkvc = $TKVC"

OUT="${OUT:-build/verify}"
mkdir -p "$OUT"

PASS=0
FAIL=0
SKIP=0

run_case() {
  local name="$1" src="$2" entry="$3" expect="$4"
  local exe="$OUT/$name.exe"
  local blog="$OUT/$name.build.log"
  local rlog="$OUT/$name.run.log"
  if [ -n "$entry" ]; then
    "$TKVC" build "$src" --entry "$entry" --out "$exe" > "$blog" 2>&1
  else
    "$TKVC" build "$src" --out "$exe" > "$blog" 2>&1
  fi
  if [ ! -f "$exe" ]; then
    echo "FAIL  $name  (build)          -> $blog"
    FAIL=$((FAIL + 1))
    return
  fi
  "$exe" > "$rlog" 2>&1
  local rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL  $name  (exit $rc)        -> $rlog"
    FAIL=$((FAIL + 1))
    return
  fi
  if ! grep -q "$expect" "$rlog"; then
    echo "FAIL  $name  (thieu '$expect')  -> $rlog"
    FAIL=$((FAIL + 1))
    return
  fi
  if grep -q "_SKIPPED" "$rlog"; then
    echo "SKIP  $name  ($expect, backend khong kha dung tren may nay)"
    SKIP=$((SKIP + 1))
  else
    echo "PASS  $name  ($expect)"
  fi
  PASS=$((PASS + 1))
}

echo "--- module selftest ---"
run_case core       TkvUI.Core.tkv     core_selftest     CORE_OK
run_case graphics   TkvUI.Graphics.tkv graphics_selftest GRAPHICS_OK
run_case text       TkvUI.Text.tkv     text_selftest     TEXT_OK
run_case effects    TkvUI.Effects.tkv  effects_selftest  EFFECTS_OK
run_case input      TkvUI.Input.tkv    input_selftest    INPUT_OK
run_case layout     TkvUI.Layout.tkv   layout_selftest   LAYOUT_OK
run_case widgets    TkvUI.Widgets.tkv  widget_selftest   WIDGETS_OK

echo "--- suite (umbrella, entry mac dinh 'main') ---"
run_case suite      TokenVector.UI.tkv ""                TKVUI_OK

echo "--- example headless ---"
run_case mobile     examples/TkvUI.DemoMobile.tkv run TKVUI_MOBILE_OK
run_case live       examples/TkvUI.Live.tkv       run TKVUI_LIVE_OK
run_case android    examples/TkvUI.AndroidDemo.tkv run ANDROID_DEMO
run_case ios        examples/TkvUI.IOSDemo.tkv     run IOS_DEMO

echo
echo "ket qua: $PASS PASS, $FAIL FAIL, $SKIP SKIPPED (log: $OUT)"
if [ $FAIL -ne 0 ]; then
  exit 1
fi
echo "TKVUI_VERIFY_OK"
