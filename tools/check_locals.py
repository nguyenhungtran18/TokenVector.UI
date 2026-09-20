"""Guard compiler: method nao > 240 locals se tran ldloc.s 1-byte.
Chay:  python3 tools/check_locals.py build/xxx.il [limit]
Exit 1 + liet ke vi pham. Quy tac: tach selftest/helper khi cham nguong.
Phat hien 2026-09-19: text_selftest 272 locals -> slot aliasing -> crash
la (NullRef) o code khong lien quan.
"""
import re
import sys

path = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 240
src = open(path, encoding="utf-8", errors="replace").read()
bad = 0
for m in re.finditer(r"\.method [^\n]*'([^']+)'\(\)", src):
    name = m.group(1)
    seg = src[m.start():m.start() + 400000]
    # method body ends at next .method at same nesting: approximate by
    # next occurrence of "\n  } // end of method" or next .method
    nxt = seg.find("\n.method", 10)
    body = seg[:nxt] if nxt > 0 else seg[:200000]
    lm = re.search(r"\.locals init \((.*?)\)", body, re.S)
    if not lm:
        continue
    parts = [p for p in lm.group(1).replace("\n", " ").split(",") if p.strip()]
    n = len(parts)
    idxs = [int(x) for x in re.findall(r"(?:ldloc|stloc)\.s\s+(\d+)", body)]
    mx = max(idxs) if idxs else 0
    if n > limit or mx > 255:
        print(f"VIOLATION {name}: locals={n} max_short_idx={mx}")
        bad += 1
if bad == 0:
    print("LOCALS_OK")
sys.exit(1 if bad else 0)
