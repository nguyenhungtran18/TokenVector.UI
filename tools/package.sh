#!/usr/bin/env bash
# Dong goi TkvUI thanh release artifact .tkvpkg (file zip + manifest + sha256).
#
#   bash tools/package.sh            -> dist/TokenVector.UI-<version>.tkvpkg (+ .sha256)
#   bash tools/package.sh --verify   -> sau khi dong goi, build suite tu ban giai nen
#
# Version doc tu tkvui.pkg.json. Artifact chua: 9 module .tkv + umbrella + manifest
# + README/LICENSE/CHANGELOG + docs + tools + examples. KHONG chua build/ (artifact dich).

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

VERSION="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' tkvui.pkg.json | head -1)"
if [ -z "$VERSION" ]; then
  echo "Khong doc duoc version tu tkvui.pkg.json" >&2
  exit 2
fi

NAME="TokenVector.UI-$VERSION"
OUT_DIR="dist"
PKG="$OUT_DIR/$NAME.tkvpkg"
STAGE="build/pkgstage"

mkdir -p "$OUT_DIR"
rm -f "$PKG" "$PKG.sha256"

# Stage: chep toan bo source vao 1 thu muc goc cung ten package, roi nen THU MUC do.
# (Compress-Archive -Path 'a','b',... khong tao directory entry -> tools nhan file
# 'docs\x' thay vi thu muc 'docs/'; stage folder + -Path <folder> cho cau truc dung.)
rm -rf "$STAGE"
mkdir -p "$STAGE/$NAME"
cp TokenVector.UI.tkv TkvUI.*.tkv tkvui.pkg.json README.md README.vi.md LICENSE CHANGELOG.md RELEASE_NOTES.md "$STAGE/$NAME/"
cp -r docs tools examples "$STAGE/$NAME/"

POWERSHELL="$(command -v powershell.exe || command -v powershell || echo powershell.exe)"
"$POWERSHELL" -NoProfile -Command "Compress-Archive -Force -Path '$STAGE\\$NAME' -DestinationPath '$NAME.tkvpkg.zip'"
if [ ! -f "$NAME.tkvpkg.zip" ]; then
  echo "Compress-Archive that bai" >&2
  exit 1
fi
mv "$NAME.tkvpkg.zip" "$PKG"

# Checksum
if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "$PKG" > "$PKG.sha256"
else
  "$POWERSHELL" -NoProfile -Command "(Get-FileHash '$PKG' -Algorithm SHA256).Hash + '  ' + (Split-Path -Leaf '$PKG')" > "$PKG.sha256"
fi

echo "Da dong goi: $PKG"
cat "$PKG.sha256"

# --verify: giai nen vao thu muc tam, build suite tu ban giai nen
if [ "${1:-}" = "--verify" ]; then
  TMP="build/pkgtest"
  rm -rf "$TMP"
  mkdir -p "$TMP"
  if command -v unzip >/dev/null 2>&1; then
    unzip -q "$PKG" -d "$TMP" 2>/dev/null
  fi
  if [ ! -f "$TMP/$NAME/tkvui.pkg.json" ]; then
    # Expand-Archive chi nhan duoi .zip -> copy tam sang .zip
    cp "$PKG" "$TMP/pkg.zip"
    "$POWERSHELL" -NoProfile -Command "Expand-Archive -Force -Path '$TMP/pkg.zip' -DestinationPath '$TMP'" >/dev/null 2>&1
    rm -f "$TMP/pkg.zip"
  fi
  if [ -f "$TMP/$NAME/tkvui.pkg.json" ]; then
    SRCDIR="$TMP/$NAME"
  elif [ -f "$TMP/tkvui.pkg.json" ]; then
    SRCDIR="$TMP"
  else
    echo "Loi: khong thay tkvui.pkg.json trong ban giai nen" >&2
    exit 1
  fi
  echo "--- build suite tu ban giai nen ($SRCDIR) ---"
  ( cd "$SRCDIR" && bash tools/verify.sh ) > "$TMP/verify.log" 2>&1
  rc=$?
  tail -3 "$TMP/verify.log"
  if [ $rc -ne 0 ]; then
    echo "Verify trong ban giai nen THAT BAI (exit $rc) - xem $TMP/verify.log" >&2
    exit 1
  fi
  echo "PKG_VERIFY_OK"
fi

exit 0
