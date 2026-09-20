#!/usr/bin/env bash
# TkvUI pack_apk: .tkv -> IL (tkvc) -> .dll (ilasm) -> APK (.NET MAUI Android).
# Headless: chi dong goi + build APK; cai len device that can `adb install`.
#
#   bash tools/pack_apk.sh [src.tkv] [entry] [outdir] [appid]
#   TKVC=... ILASM=... DOTNET=... bash tools/pack_apk.sh TkvUI.Data.tkv data_selftest build/apk com.tokenvector.demo
#
# Yeu cau: tkvc.exe, ilasm.exe, dotnet 8 + workload maui, JDK 17 + Android SDK
# (ANDROID_HOME hoac ANDROID_SDK_ROOT). Thieu -> SKIP (exit 3) kem huong dan.
# Entry phai khong tham so, tra ve str. UI that tren device can them JNI shim
# (xem TkvUI.Platform Android host-driven contract + examples/TkvUI.AndroidDemo).

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

ILASM="${ILASM:-}"
if [ -z "$ILASM" ]; then
  for d in "/c/WINDOWS/Microsoft.NET/Framework64/v4.0.30319" "/c/WINDOWS/Microsoft.NET/Framework/v4.0.30319"; do
    if [ -x "$d/ilasm.exe" ]; then ILASM="$d/ilasm.exe"; break; fi
  done
fi
if [ -z "$ILASM" ] || [ ! -x "$ILASM" ]; then
  echo "SKIP: khong thay ilasm.exe (dat ILASM=...). Can .NET Framework 4.x." >&2
  exit 3
fi

DOTNET="${DOTNET:-$(command -v dotnet 2>/dev/null || command -v dotnet.exe 2>/dev/null || true)}"
need() {
  if [ -z "$DOTNET" ]; then echo "SKIP: thieu .NET 8 SDK ($1)" >&2; exit 3; fi
}
need "dotnet"
if ! "$DOTNET" workload list 2>/dev/null | grep -q "maui"; then
  echo "SKIP: thieu workload maui. Chay: dotnet workload install maui" >&2
  exit 3
fi
if [ -z "${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}" ]; then
  echo "SKIP: thieu Android SDK. Dat ANDROID_HOME (Android Studio > SDK Manager)." >&2
  exit 3
fi
if ! command -v java >/dev/null 2>&1 && ! command -v java.exe >/dev/null 2>&1; then
  echo "SKIP: thieu JDK 17 (can cho Gradle/Android build)." >&2
  exit 3
fi

SRC="${1:-TkvUI.Data.tkv}"
ENTRY="${2:-data_selftest}"
OUT="${3:-build/apk}"
APPID="${4:-com.tokenvector.demo}"
CLASS="${CLASS:-TKVApp}"
ASM="${ASM:-TKVApp}"

STAGE="$OUT/stage"
APPD="$OUT/app"
mkdir -p "$STAGE" "$APPD"
NAME="$(basename "$SRC" .tkv)"

echo "[1/4] tkvc build $SRC ($ENTRY)"
"$TKVC" build "$SRC" --entry "$ENTRY" --out "$STAGE/app.exe"
if [ ! -f "$STAGE/app.il" ]; then
  echo "FAIL: khong thay app.il do tkvc sinh" >&2
  exit 1
fi

echo "[2/4] ilasm /dll"
MSYS_NO_PATHCONV=1 "$ILASM" "$STAGE/app.il" /dll "/output:$STAGE/$ASM.dll"
if [ ! -f "$STAGE/$ASM.dll" ]; then
  echo "FAIL: ilasm khong tao $ASM.dll" >&2
  exit 1
fi

echo "[3/4] scaffold MAUI single-project ($APPID)"
rm -rf "$APPD"
"$DOTNET" new maui -o "$APPD" -n TkvApk || { echo "FAIL: dotnet new maui" >&2; exit 1; }
# Trang hien ket qua entry (headless-safe, khong can GPU/device khi chay test).
cat > "$APPD/MainPage.xaml.cs" <<EOF
namespace TkvApk;
public partial class MainPage : ContentPage
{
    public MainPage()
    {
        InitializeComponent();
        ResultLabel.Text = $CLASS.$ENTRY();
    }
}
EOF
if ! grep -q "ResultLabel" "$APPD/MainPage.xaml"; then
  python3 - "$APPD/MainPage.xaml" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
s = s.replace("</VerticalStackLayout>", '    <Label x:Name="ResultLabel" Text="..." />\n</VerticalStackLayout>')
open(p, "w", encoding="utf-8").write(s)
PYEOF
fi
# Tham chieu DLL do tkvc/ilasm sinh.
if command -v python3 >/dev/null 2>&1; then
  python3 - "$APPD/TkvApk.csproj" "$ASM" <<'PYEOF'
import sys
p, asm = sys.argv[1], sys.argv[2]
s = open(p, encoding="utf-8").read()
ref = '  <ItemGroup><Reference Include="%s"><HintPath>../stage/%s.dll</HintPath></Reference></ItemGroup>\n</Project>' % (asm, asm)
s = s.replace("</Project>", ref)
open(p, "w", encoding="utf-8").write(s)
PYEOF
fi

echo "[4/4] dotnet publish -f net8.0-android"
(cd "$APPD" && "$DOTNET" publish -f net8.0-android -c Release -p:ApplicationId="$APPID") || { echo "FAIL: publish android" >&2; exit 1; }
APK="$(find "$APPD" -name "*-Signed.apk" | head -1)"
if [ -z "$APK" ]; then
  echo "FAIL: khong thay APK signed" >&2
  exit 1
fi
cp "$APK" "$OUT/app.apk"
echo "APK: $OUT/app.apk"
echo "Cai len device: adb install -r $OUT/app.apk"
echo "TKVUI_APK_OK"
