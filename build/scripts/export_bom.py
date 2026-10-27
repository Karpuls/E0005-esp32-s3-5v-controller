#!/usr/bin/env python3
"""BOM grouped from the schematic fields (all sheets) -> build/out/E0005_bom_from_sch.csv"""
import os, sys, glob, csv, re, collections
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, find, findall
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
g = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(PROJ, '*.kicad_sch'))):
    for s in findall(parse(open(f).read()), 'symbol'):
        if find(s, 'lib_id')[1].startswith('power:') or find(s, 'in_bom')[1] != 'yes':
            continue
        pr = {p[1]: p[2] for p in findall(s, 'property')}
        k = (pr['Value'], pr['Footprint'].split(':')[-1], pr.get('MPN', ''), pr.get('Manufacturer', ''),
             pr.get('Supplier', ''), pr.get('Supplier PN', ''), 'DNP' if find(s, 'dnp')[1] == 'yes' else '')
        g.setdefault(k, []).append(pr['Reference'])
key = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
with open(os.path.join(PROJ, 'build', 'out', 'E0005_bom_from_sch.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['Qty', 'References', 'Value', 'Footprint', 'MPN', 'Manufacturer', 'Supplier', 'Supplier PN', 'DNP'])
    for k, refs in sorted(g.items(), key=lambda kv: key(sorted(kv[1], key=key)[0])):
        w.writerow([len(refs), ' '.join(sorted(refs, key=key))] + list(k))
print(sum(len(v) for v in g.values()), 'parts in', len(g), 'lines')
