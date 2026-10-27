# dv.py [types...] : DRC violations (board-local coords), skipping unconnected/via_dangling unless asked
import re, sys
skip = {'unconnected_items', 'via_dangling', 'lib_footprint_mismatch'}
want = set(sys.argv[1:])
t = open('drc.rpt').read().split('\n[')
for b in t[1:]:
    k = b.split(']')[0]
    if (want and k not in want) or (not want and k in skip): continue
    lines = b.split('\n')
    out = [k + ': ' + lines[0].split(':', 1)[1].strip()[:90]]
    for l in lines[1:]:
        m = re.match(r'\s+@\(([\d.]+) mm, ([\d.]+) mm\): (.*)', l)
        if m: out.append('   (%.2f,%.2f) %s' % (float(m.group(1)) - 150, float(m.group(2)) - 100, m.group(3)[:100]))
    print('\n'.join(out))
