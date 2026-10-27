#!/usr/bin/env python3
"""Compare E0005 references with E0003: same ref should be the same part unless the change is intended."""
import os, re, glob, sys
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, find, findall
E3 = '/home/karpulis/KiCad/E0003 - ESP32 control box mainboard'
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
def refs(d):
    out = {}
    for f in glob.glob(os.path.join(d, '*.kicad_sch')):
        for s in findall(parse(open(f).read()), 'symbol'):
            if find(s, 'lib_id') is None or find(s, 'lib_id')[1].startswith('power:'):
                continue
            pr = {p[1]: p[2] for p in findall(s, 'property')}
            out[pr['Reference']] = (pr['Value'], pr['Footprint'].split(':')[-1])
    return out
a, b = refs(E3), refs(PROJ)
key = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
print('same ref, different part:')
for r in sorted(set(a) & set(b), key=key):
    if a[r] != b[r]:
        print('  %-5s %-28s -> %s' % (r, '%s %s' % a[r], '%s %s' % b[r]))
print('removed:', ' '.join(sorted(set(a) - set(b), key=key)))
print('new:    ', ' '.join(sorted(set(b) - set(a), key=key)))
