#!/usr/bin/env bash
# TkvUI pack_app: tuong duong `tkvc --package` (cho den khi compiler ho tro
# native): build 1 entry .tkv -> EXE don file + manifest + sha256 trong dist/.
#
#   bash tools/pack_app.sh examples/TkvUI.PrintDemo.tkv printdemo_run [appname] [outdir]
#
# Output: <outdir>/<appname>/  (appname.exe + README.txt + MANIFEST.txt + .sha256)
# Single-file: tkvc sinh EXE doc lap (IL embed, chi can .NET Framework/Mono host).

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
echo "tkvc = $TKVC"

SRC="${1:-}"
ENTRY="${2:-}"
APP="${3:-}"
OUT="${4:-dist}"

if [ -z "$SRC" ] || [ -z "$ENTRY" ]; then
  echo "Dung: bash tools/pack_app.sh <src.tkv> <entry> [appname] [outdir]" >&2
  exit 2
fi
if [ ! -f "$SRC" ]; then
  echo "Khong thay source: $SRC" >&2
  exit 2
fi
if [ -z "$APP" ]; then
  APP="$(basename "$SRC" .tkv)"
fi

VERSION="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' tkvui.pkg.json | head -1)"
if [ -z "$VERSION" ]; then VERSION="0.0.0"; fi

STAGE="$OUT/$APP"
EXE="$STAGE/$APP.exe"
mkdir -p "$STAGE"

echo "[1/3] tkvc build $SRC ($ENTRY)"
"$TKVC" build "$SRC" --entry "$ENTRY" --out "$EXE"
if [ ! -f "$EXE" ]; then
  echo "FAIL: build khong tao $EXE" >&2
  exit 1
fi

echo "[2/3] manifest + readme"
rm -f "$STAGE/$APP.il"
SIZE="$(wc -c < "$EXE" | tr -d ' ')"
cat > "$STAGE/MANIFEST.txt" <<EOF
name=$APP
version=$VERSION
entry=$ENTRY
src=$SRC
exe=$APP.exe
size_bytes=$SIZE
runtime=dotnet-framework-or-mono
built_with=tkvc
EOF
cat > "$STAGE/README.txt" <<EOF
$APP (TokenVector.UI v$VERSION)
Chay: $APP.exe   (can .NET Framework 4.x tren Windows, hoac Mono)
Entry: $ENTRY  (nguon: $SRC)
EOF

echo "[3/3] sha256"
if command -v sha256sum >/dev/null 2>&1; then
  ( cd "$STAGE" && sha256sum "$APP.exe" > "$APP.exe.sha256" )
else
  powershell -NoProfile -Command "(Get-FileHash '$EXE' -Algorithm SHA256).Hash + '  $APP.exe'" > "$STAGE/$APP.exe.sha256"
fi
cat "$STAGE/$APP.exe.sha256"

echo "APP_PACKAGE_OK: $STAGE (${SIZE} bytes)"
