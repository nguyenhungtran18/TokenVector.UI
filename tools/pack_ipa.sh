#!/usr/bin/env bash
# TkvUI pack_ipa: .tkv -> IL (tkvc) -> .dll (ilasm) -> IPA (.NET MAUI iOS).
# Headless: chi dong goi + build IPA (can ky so that de cai len device).
#
#   bash tools/pack_ipa.sh [src.tkv] [entry] [outdir] [bundleid]
#   TKVC=... ILASM=... DOTNET=... bash tools/pack_ipa.sh TkvUI.Data.tkv data_selftest build/ipa com.tokenvector.demo
#
# Yeu cau BAT BUOC: macOS + Xcode (xcodebuild) + .NET 8 + workload maui.
# Chay tren Windows/Linux -> SKIP (exit 3). UI that tren device can them
# shim Swift/ObjC (xem TkvUI.Platform iOS host-driven contract).
# Ky so: truyen CODESIGN_KEY="iPhone Developer: ..." (+ PROVISION) de tao IPA
# cai duoc; neu khong, chi build .app (simulator/device unsigned).

set -u

if [ "$(uname)" != "Darwin" ]; then
  echo "SKIP: pack_ipa chi chay tren macOS (can Xcode + codesign). May hien tai: $(uname)." >&2
  exit 3
fi
if ! command -v xcodebuild >/dev/null 2>&1; then
  echo "SKIP: thieu Xcode (xcodebuild). Cai tu App Store + `xcode-select --install`." >&2
  exit 3
fi

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TKVC="${TKVC:-/d/TokenVector/3.code/dist/tkvc.exe}"
if [ ! -x "$TKVC" ]; then
  TKVC="$(command -v tkvc.exe 2>/dev/null || command -v tkvc 2>/dev/null || true)"
fi
if [ -z "$TKVC" ] || [ ! -x "$TKVC" ]; then
  echo "Khong tim thay tkvc.exe (can ban macOS). Dat TKVC=..." >&2
  exit 2
fi

DOTNET="${DOTNET:-$(command -v dotnet 2>/dev/null || true)}"
if [ -z "$DOTNET" ]; then
  echo "SKIP: thieu .NET 8 SDK." >&2
  exit 3
fi
if ! "$DOTNET" workload list 2>/dev/null | grep -q "maui"; then
  echo "SKIP: thieu workload maui. Chay: dotnet workload install maui" >&2
  exit 3
fi

SRC="${1:-TkvUI.Data.tkv}"
ENTRY="${2:-data_selftest}"
OUT="${3:-build/ipa}"
BUNDLEID="${4:-com.tokenvector.demo}"
CLASS="${CLASS:-TKVApp}"
ASM="${ASM:-TKVApp}"

STAGE="$OUT/stage"
APPD="$OUT/app"
mkdir -p "$STAGE" "$APPD"

echo "[1/4] tkvc build $SRC ($ENTRY)"
"$TKVC" build "$SRC" --entry "$ENTRY" --out "$STAGE/app.exe"
if [ ! -f "$STAGE/app.il" ]; then
  echo "FAIL: khong thay app.il do tkvc sinh" >&2
  exit 1
fi

echo "[2/4] ilasm /dll"
"$DOTNET" tool run ilasm 2>/dev/null || true
ILASM_MAC="$(find ~/.dotnet/tools /usr/local/share/dotnet -name ilasm 2>/dev/null | head -1)"
if [ -z "$ILASM_MAC" ]; then
  echo "SKIP: thieu ilasm tren mac (dotnet tool install -g dotnet-ilasm)." >&2
  exit 3
fi
"$ILASM_MAC" "$STAGE/app.il" /dll "/output:$STAGE/$ASM.dll"
if [ ! -f "$STAGE/$ASM.dll" ]; then
  echo "FAIL: ilasm khong tao $ASM.dll" >&2
  exit 1
fi

echo "[3/4] scaffold MAUI single-project ($BUNDLEID)"
rm -rf "$APPD"
"$DOTNET" new maui -o "$APPD" -n TkvIpa || { echo "FAIL: dotnet new maui" >&2; exit 1; }
cat > "$APPD/MainPage.xaml.cs" <<EOF
namespace TkvIpa;
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        ResultLabel.Text = $CLASS.$ENTRY();
    }
}
EOF

echo "[4/4] dotnet build -f net8.0-ios"
SIGN_ARGS=""
if [ -n "${CODESIGN_KEY:-}" ]; then
  SIGN_ARGS="-p:CodesignKey=\"$CODESIGN_KEY\""
  if [ -n "${PROVISION:-}" ]; then
    SIGN_ARGS="$SIGN_ARGS -p:CodesignProvision=\"$PROVISION\""
  fi
fi
# shellcheck disable=SC2086
(cd "$APPD" && "$DOTNET" build -f net8.0-ios -c Release $SIGN_ARGS) || { echo "FAIL: build ios" >&2; exit 1; }
APP="$(find "$APPD" -name "*.app" -maxdepth 6 | head -1)"
if [ -z "$APP" ]; then
  echo "FAIL: khong thay .app" >&2
  exit 1
fi
if [ -n "${CODESIGN_KEY:-}" ]; then
  (cd "$(dirname "$APP")" && mkdir -p Payload && cp -r "$(basename "$APP")" Payload/ && zip -r "$ROOT/$OUT/app.ipa" Payload) || { echo "FAIL: dong IPA" >&2; exit 1; }
  echo "IPA: $OUT/app.ipa"
else
  echo "APP (chua ky, can CODESIGN_KEY de dong IPA): $APP"
fi
echo "TKVUI_IPA_OK"
