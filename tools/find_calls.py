import re

src = open("build/native_test.il", encoding="utf-8", errors="replace").read()
for name in ["sbr", "tabx"]:
    print("=" * 20, name)
for m in re.finditer(r"call[^\n]*render[^\n]*", src):
    print(m.group(0)[:200])
