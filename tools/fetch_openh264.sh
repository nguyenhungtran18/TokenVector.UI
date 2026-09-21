#!/usr/bin/env bash
# Twin cua fetch_openh264.ps1 cho Git Bash/WSL. Chay: bash tools/fetch_openh264.sh [version]
set -u
VER="${1:-2.6.0}"
OUTDIR="build"
mkdir -p "$OUTDIR"
URL="https://ciscobinary.openh264.org/openh264-${VER}-win64.dll.bz2"
echo "GET $URL"
curl -sL --max-time 120 -o "$OUTDIR/openh264-win64.dll.bz2" "$URL"
python3 -c "import bz2; open('$OUTDIR/openh264-win64.dll','wb').write(bz2.decompress(open('$OUTDIR/openh264-win64.dll.bz2','rb').read())); print('extract ok')"
python3 - "$OUTDIR/openh264-win64.dll" <<'PYEOF'
import sys
p = sys.argv[1]
d = open(p, 'rb').read()
assert len(d) > 500000, len(d)
assert d[:2] == b'MZ', d[:2]
for fn in (b'WelsCreateDecoder', b'WelsCreateSVCEncoder', b'WelsDestroyDecoder'):
    assert fn in d, fn
    print('export ok:', fn.decode())
print('OPENH264_OK (%s, %d bytes)' % (p, len(d)))
PYEOF
