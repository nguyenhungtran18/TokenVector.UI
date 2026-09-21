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
run_case media      TkvUI.Media.tkv    media_selftest     MEDIA_OK
run_case bidi       TkvUI.Bidi.tkv     bidi_selftest     BIDI_OK
run_case gpu        TkvUI.Gpu.tkv      gpu_selftest      GPU_OK
run_case a11y       TkvUI.A11y.tkv     a11y_selftest     A11Y_OK
run_case shaping    TkvUI.Shaping.tkv  shaping_selftest  SHAPING_OK
run_case fontdisc   TkvUI.FontDiscovery.tkv fd_selftest  FONTDISCOVERY_OK
run_case theme      TkvUI.Theme.tkv    theme_selftest    THEME_OK
run_case native     TkvUI.Widgets.Native.tkv native_selftest NATIVE_OK
run_case data       TkvUI.Data.tkv     data_selftest     DATA_OK
run_case sqlite     TkvUI.SQLite.tkv   sqlite_selftest   SQLITE_OK
run_case printing   TkvUI.Printing.tkv printing_selftest PRINTING_OK
run_case abridge    TkvUI.A11yBridge.tkv abridge_selftest ABRIDGE_OK
run_case font       TkvUI.FontFallback.tkv fallback_selftest FALLBACK_OK
run_case emoji      TkvUI.EmojiData.tkv emoji_selftest EMOJIDATA_OK
run_case kittest    TkvUI.KitTest.tkv kittest_selftest KITTEST_OK
run_case nativedlg  TkvUI.NativeDlg.tkv nativedlg_selftest NATIVEDLG_OK
run_case ime        TkvUI.Ime.tkv ime_selftest IME_OK
run_case uia        TkvUI.Uia.tkv uia_selftest UIA_OK
run_case atspi      TkvUI.Atspi.tkv atspi_selftest ATSPI_OK

echo "--- suite (umbrella, entry mac dinh 'main') ---"
run_case suite      TokenVector.UI.tkv ""                TKVUI_OK

echo "--- example headless ---"
run_case mobile     examples/TkvUI.DemoMobile.tkv run TKVUI_MOBILE_OK
run_case live       examples/TkvUI.Live.tkv       run TKVUI_LIVE_OK
run_case mediademo  examples/TkvUI.MediaDemo.tkv  run TKVUI_MEDIA_DEMO_OK
run_case android    examples/TkvUI.AndroidDemo.tkv run ANDROID_DEMO
run_case ios        examples/TkvUI.IOSDemo.tkv     run IOS_DEMO
run_case phase1     examples/TkvUI.Phase1Demo.tkv phase1_run PHASE1_OK
run_case printdemo  examples/TkvUI.PrintDemo.tkv printdemo_run PRINTDEMO_OK
run_case abdemo     examples/TkvUI.A11yDemo.tkv abdemo_run ABDEMO_OK
run_case designer   examples/TkvUI.Designer.tkv designer_run DESIGNER_OK
run_case cruddemo   examples/TkvUI.CrudDemo.tkv crud_run CRUD_TKVUI_OK
run_case browser    examples/TkvUI.BrowserDemo.tkv browser_run BROWSER_OK
run_case animdemo   examples/TkvUI.AnimDemo.tkv anim_run ANIM_OK
run_case fuzz       examples/TkvUI.Fuzz.tkv fuzz_run FUZZ_OK
run_case designerapp examples/TkvUI.Designer.tkv designer_app_test DESIGNER_APP_OK

echo
echo "ket qua: $PASS PASS, $FAIL FAIL, $SKIP SKIPPED (log: $OUT)"
if [ $FAIL -ne 0 ]; then
  exit 1
fi
echo "TKVUI_VERIFY_OK"
