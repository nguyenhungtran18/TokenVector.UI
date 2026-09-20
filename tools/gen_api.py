import json
import re
import os
import sys

os.chdir(os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), ".."))
pkg = json.load(open('tkvui.pkg.json', encoding='utf-8'))
mods = {m['file']: m for m in pkg['modules']}

out = []
out.append('# TkvUI API Index (sinh ban-tu-dong — sua tay phan mo ta)')
out.append('')
out.append('> Tra cuu nhanh theo module. Chi tiet xem source + selftest entry.')
out.append('> Sinh boi `tools/gen_api.py`-style (xem cuoi file). Quy uoc compiler: xem `docs/TkvUI.Roadmap.md` section 0.')
out.append('')
total_f = 0
total_c = 0
for f in sorted(mods):
    m = mods[f]
    src = open(f, encoding='utf-8').read()
    funcs = re.findall(r'^def ([A-Za-z_][A-Za-z0-9_]*)', src, re.M)
    classes = re.findall(r'^class ([A-Za-z_][A-Za-z0-9_]*)', src, re.M)
    total_f += len(funcs)
    total_c += len(classes)
    out.append('## ' + m['name'] + ' (`' + f + '`)')
    out.append('')
    out.append(m.get('summary', ''))
    out.append('')
    st = m.get('selftest')
    out.append('selftest: `' + (st if st else '(khong co — data-only)') + '`'
               + ('  ' if False else ''))
    out.append('')
    if classes:
        out.append('Classes: ' + ', '.join('`' + c + '`' for c in classes))
        out.append('')
    pub = [x for x in funcs if not x.startswith('_') and not x.endswith('_selftest')]
    out.append('Functions (%d): %s' % (len(pub), ', '.join('`' + x + '`' for x in pub[:60])))
    if len(pub) > 60:
        out.append('')
        out.append('(...+%d, xem source)' % (len(pub) - 60))
    out.append('')
out.append('---')
out.append('Tong: %d modules, %d classes, %d functions.' % (len(mods), total_c, total_f))
open('docs/API.md', 'w', encoding='utf-8').write(chr(10).join(out) + chr(10))
print('modules:', len(mods), 'classes:', total_c, 'funcs:', total_f)
