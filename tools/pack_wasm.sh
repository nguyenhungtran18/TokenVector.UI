#!/usr/bin/env bash
# TkvUI pack_wasm: .tkv -> IL (tkvc) -> .dll (ilasm /dll) -> WASI .wasm (dotnet publish wasi-wasm).
# Headless: khong mo cua so, khong can device/GPU. Tu chay thu bang wasmtime neu co.
#
#   bash tools/pack_wasm.sh [src.tkv] [entry] [outdir] [expect]
#   TKVC=... ILASM=... WASMTIME=... CLASS=TKVApp ASM=TKVApp AOT=0 TARGET=wasi \
#     bash tools/pack_wasm.sh TkvUI.Bidi.tkv bidi_selftest build/wasm BIDI_OK
#
# Yeu cau: tkvc.exe, ilasm.exe (.NET Framework 4.x), dotnet 8 + workload wasi-experimental.
# wasmtime (optional, de chay thu WASI): https://github.com/bytecodealliance/wasmtime/releases
# Luu y: entry phai khong tham so, tra ve str (vd cac ham *_selftest).
# AOT=1: bien dich native AOT (can wasi-sdk: WASI_SDK_PATH hoac build/wasisdk/wasi-sdk-25.0-x86_64-windows).
#   LUU Y (kiem chung 2026-09-18): tren .NET 8.0.425 + wasi-experimental 8.0.31,
#   publish AOT van ra dotnet.wasm giong he interpreter (hash bang nhau) — native
#   AOT chua that su engage, can dieu tra upstream (co the can .NET 9+ nhu plan).
#   Mac dinh dung AOT=0 (interpreter, da verify chay that bang wasmtime).
# AOT=0 (mac dinh): interpreter bundle, khong can toolchain native, build vai giay.
# TARGET=wasi (mac dinh): console WASI, chay thu duoc bang wasmtime.
# TARGET=browser: Blazor WASM host (can workload wasm-tools); chi verify publish + file _framework,
#   chay that can browser (mo wwwroot bang web server, vd: npx serve publish/wwwroot).

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# dotnet.exe chay dang Windows (interop): doi ROOT sang Windows path de
# truyen -o (WSL path /mnt/d/... bi dotnet hieu thanh D:\mnt\d\... rac).
ROOTW="$ROOT"
if command -v wslpath >/dev/null 2>&1; then
  case "$ROOT" in
    /mnt/*) ROOTW="$(wslpath -w "$ROOT")" ;;
  esac
fi

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
  echo "Khong tim thay ilasm.exe. Dat ILASM=/duong/dan/ilasm.exe" >&2
  exit 2
fi

DOTNET="${DOTNET:-$(command -v dotnet 2>/dev/null || command -v dotnet.exe 2>/dev/null || true)}"
if [ -z "$DOTNET" ]; then
  echo "Khong tim thay dotnet. Can .NET 8 SDK." >&2
  exit 2
fi
if ! "$DOTNET" workload list 2>/dev/null | grep -q "wasi-experimental"; then
  echo "Thieu workload wasi-experimental. Chay: dotnet workload install wasi-experimental" >&2
  exit 2
fi

SRC="${1:-TkvUI.Bidi.tkv}"
ENTRY="${2:-bidi_selftest}"
OUT="${3:-build/wasm}"
EXPECT="${4:-}"
CLASS="${CLASS:-TKVApp}"
ASM="${ASM:-TKVApp}"
AOT="${AOT:-0}"
TARGET="${TARGET:-wasi}"
TFM="${TFM:-net8.0}"
if [ "$AOT" = "1" ]; then
  CFG="Release"
  AOTVAL="true"
  if [ -z "${WASI_SDK_PATH:-}" ]; then
    if [ -x "$ROOT/build/wasisdk/wasi-sdk-25.0-x86_64-windows/bin/clang.exe" ]; then
      export WASI_SDK_PATH="$(cd "$ROOT/build/wasisdk/wasi-sdk-25.0-x86_64-windows" && pwd -W)"
    else
      echo "AOT=1 can wasi-sdk: dat WASI_SDK_PATH hoac giai nen wasi-sdk vao build/wasisdk/" >&2
      exit 2
    fi
  fi
  echo "AOT native: WASI_SDK_PATH=$WASI_SDK_PATH"
else
  CFG="Debug"
  AOTVAL="false"
fi

STAGE="$OUT/stage"
HOSTD="$OUT/host"
PUBD="$OUT/publish"
mkdir -p "$STAGE" "$HOSTD" "$PUBD"

NAME="$(basename "$SRC" .tkv)"

echo "[1/5] tkvc build $SRC ($ENTRY)"
"$TKVC" build "$SRC" --entry "$ENTRY" --out "$STAGE/app.exe"
IL="$STAGE/app.il"
if [ ! -f "$IL" ]; then
  echo "FAIL: khong thay $IL do tkvc sinh" >&2
  exit 1
fi

echo "[2/5] ilasm /dll -> $ASM.dll"
# Ten file DLL phai khop ten assembly trong IL (mac dinh TKVApp) de runtime tim thay trong managed/.
# MSYS (git-bash) tu bien tham so "/dll" thanh path Windows -> tat pathconv cho lenh ilasm.
MSYS_NO_PATHCONV=1 "$ILASM" "$IL" /dll "/output:$STAGE/$ASM.dll"
if [ ! -f "$STAGE/$ASM.dll" ]; then
  echo "FAIL: ilasm khong tao $ASM.dll" >&2
  exit 1
fi

if [ "$TARGET" = "browser" ]; then
  # Phase 7.3: canvas demo — TKVApp render base64 RGBA, JS putImageData, rAF loop.
  # Can module co BROWSER_FRAME(f: i32)->str + BROWSER_INFO()->str
  # (vd examples/TkvUI.BrowserDemo.tkv). Kiem tra that bang Chrome headless.
  BROWSER_FRAME="${BROWSER_FRAME:-browser_frame}"
  BROWSER_INFO="${BROWSER_INFO:-browser_info}"
  echo "[3/5] scaffold Blazor canvas host ($CLASS.$BROWSER_FRAME)"
  rm -rf "$HOSTD"
  "$DOTNET" new blazorwasm -o "$HOSTD" --no-https || { echo "FAIL: dotnet new blazorwasm" >&2; exit 1; }
  sed -i "s|</Project>|  <ItemGroup><Reference Include=\"$ASM\"><HintPath>../stage/$ASM.dll</HintPath></Reference></ItemGroup>\n</Project>|" "$HOSTD/host.csproj" || { echo "FAIL: them Reference" >&2; exit 1; }
  cat > "$HOSTD/TkvBridge.cs" <<EOF
using Microsoft.JSInterop;
public static class TkvBridge
{
    [JSInvokable]
    public static string GetFrame(int f) { return $CLASS.$BROWSER_FRAME(f); }
    [JSInvokable]
    public static string GetInfo() { return $CLASS.$BROWSER_INFO(); }
}
EOF
  mkdir -p "$HOSTD/wwwroot/js"
  cat > "$HOSTD/wwwroot/js/tkv.js" <<'JSEOF'
window.tkv = {
  canvas: null, ctx: null, img: null,
  init(id, w, h) {
    this.canvas = document.getElementById(id);
    this.ctx = this.canvas.getContext("2d");
    this.img = this.ctx.createImageData(w, h);
    window.__tkvFrames = 0;
    window.__tkvReady = false;
  },
  async frame(f) {
    const b64 = await DotNet.invokeMethodAsync("host", "GetFrame", f);
    const bin = atob(b64);
    const d = this.img.data;
    for (let i = 0; i < bin.length; i++) d[i] = bin.charCodeAt(i);
    this.ctx.putImageData(this.img, 0, 0);
    window.__tkvFrames = f + 1;
    window.__tkvReady = true;
    const tag = document.getElementById("tkvframe");
    if (tag) tag.textContent = "frame=" + (f + 1);
    return window.__tkvFrames;
  },
  loop() {
    let f = 0;
    const tick = () => { this.frame(f++); requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
  }
};
JSEOF
  cat > "$HOSTD/Pages/Home.razor" <<EOF
@page "/"
@inject IJSRuntime JS

<PageTitle>TkvUI on WebAssembly (canvas)</PageTitle>

<h1>TokenVector.UI chay trong Browser (Blazor WASM + canvas)</h1>
<canvas id="tkv" width="160" height="90" style="width:480px;height:270px;image-rendering:pixelated;border:1px solid #888"></canvas>
<p><span id="tkvframe">frame=0</span> <code>@info</code></p>

@code {
    string info = "";
    protected override async Task OnAfterRenderAsync(bool first)
    {
        if (!first) return;
        info = TkvBridge.GetInfo();
        StateHasChanged();
        await JS.InvokeVoidAsync("tkv.init", "tkv", 160, 90);
        await JS.InvokeVoidAsync("tkv.loop");
    }
}
EOF
  python3 - "$HOSTD/wwwroot/index.html" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
tag = '<script src="js/tkv.js"></script>'
if "js/tkv.js" not in s:
    s = s.replace("</body>", "    " + tag + "\n</body>")
open(p, "w", encoding="utf-8").write(s)
PYEOF
  echo "[4/5] dotnet publish blazor-wasm"
  (cd "$HOSTD" && "$DOTNET" publish -c Release -o "../publish") || { echo "FAIL: dotnet publish" >&2; exit 1; }
  FW="$PUBD/wwwroot/_framework"
  # Blazor AOT tung assembly rieng: code TokenVector nam trong $ASM.wasm (native).
  if [ ! -f "$FW/$ASM.wasm" ]; then
    echo "FAIL: khong thay $ASM.wasm trong $FW" >&2
    exit 1
  fi
  if ! grep -q "$ASM" "$FW/blazor.boot.json"; then
    echo "FAIL: blazor.boot.json khong tham chieu $ASM" >&2
    exit 1
  fi
  if ! ls "$FW"/dotnet.*.js "$FW"/dotnet.native.wasm >/dev/null 2>&1; then
    echo "FAIL: thieu dotnet runtime trong $FW" >&2
    exit 1
  fi
  echo "BROWSER bundle: $PUBD/wwwroot ($ASM.wasm AOT + dotnet.native.wasm)"
  echo "Chay that: mo $PUBD/wwwroot/index.html qua web server (vd: npx serve $PUBD/wwwroot)"
  echo "TKVUI_WASM_OK"
  exit 0
fi

echo "[3/5] scaffold dotnet host ($CLASS.$ENTRY)"
# csproj theo dung template chinh chu `dotnet new wasiconsole` + Reference toi DLL do tkvc/ilasm sinh.
cat > "$HOSTD/host.csproj" <<EOF
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>$TFM</TargetFramework>
    <RuntimeIdentifier>wasi-wasm</RuntimeIdentifier>
    <OutputType>Exe</OutputType>
    <PublishTrimmed>true</PublishTrimmed>
    <RunAOTCompilation>$AOTVAL</RunAOTCompilation>
    <RunAOTCompilationAfterBuild>$AOTVAL</RunAOTCompilationAfterBuild>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="$ASM">
      <HintPath>../stage/$ASM.dll</HintPath>
    </Reference>
  </ItemGroup>
</Project>
EOF
cat > "$HOSTD/Program.cs" <<EOF
using System;

class WasmHost
{
    static void Main(string[] args)
    {
        Console.WriteLine($CLASS.$ENTRY());
    }
}
EOF

rm -rf "$OUT/appbundle"
mkdir -p "$OUT/appbundle"
if [ "$AOT" = "1" ]; then
  # AOT chi chay o publish (khong chay o build): dotnet publish Release -> bundle chay that.
  echo "[4/5] dotnet publish wasi-wasm Release (AOT native)"
  (cd "$HOSTD" && "$DOTNET" publish -c Release -p:RunAOTCompilation=true -o "$ROOTW/$OUT/appbundle") || { echo "FAIL: dotnet publish" >&2; exit 1; }
else
  echo "[4/5] dotnet build wasi-wasm $CFG (interpreter)"
  (cd "$HOSTD" && "$DOTNET" build -c "$CFG") || { echo "FAIL: dotnet build" >&2; exit 1; }
  APPBUNDLE="$HOSTD/bin/$CFG/net8.0/wasi-wasm/AppBundle"
  if [ ! -f "$APPBUNDLE/dotnet.wasm" ]; then
    echo "FAIL: khong thay dotnet.wasm trong $APPBUNDLE" >&2
    exit 1
  fi
  cp -r "$APPBUNDLE/." "$OUT/appbundle"/
fi
echo "WASM bundle: $OUT/appbundle"

if [ -n "$EXPECT" ]; then
  WASMTIME="${WASMTIME:-$(command -v wasmtime 2>/dev/null || true)}"
  if [ -z "$WASMTIME" ] || [ ! -x "$WASMTIME" ]; then
    echo "SKIP chay thu: khong thay wasmtime (dat WASMTIME=...)"
    exit 0
  fi
  case "$WASMTIME" in
    */*) WASMTIME="$(cd "$(dirname "$WASMTIME")" && pwd)/$(basename "$WASMTIME")" ;;
  esac
  echo "[5/5] wasmtime run --dir . ./dotnet.wasm host (expect '$EXPECT')"
  # Theo run-wasmtime.sh do template sinh: chay dotnet.wasm trong AppBundle,
  # truyen ten entry assembly ("host") lam argv; managed/ + icudt.dat can --dir + cwd dung.
  (cd "$OUT/appbundle" && "$WASMTIME" run --dir . ./dotnet.wasm host) > "$OUT/run.log" 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then
    echo "FAIL: wasmtime exit $rc"
    tail -20 "$OUT/run.log"
    exit 1
  fi
  if ! grep -q "$EXPECT" "$OUT/run.log"; then
    echo "FAIL: thieu '$EXPECT'"
    tail -20 "$OUT/run.log"
    exit 1
  fi
  echo "PASS wasmtime ($EXPECT)"
fi
echo "TKVUI_WASM_OK"
