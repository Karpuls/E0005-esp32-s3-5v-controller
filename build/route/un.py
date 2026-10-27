import re,collections,sys
t=open('drc.rpt').read()
d=collections.defaultdict(list)
for m in re.finditer(r'\[unconnected_items\][^\n]*\n[^\n]*\n((?:\s+@[^\n]*\n)+)',t):
    for l in m.group(1).strip().split('\n'):
        mm=re.search(r'@\(([-\d.]+) mm, ([-\d.]+) mm\): (.*)',l)
        x,y=float(mm.group(1))-150,float(mm.group(2))-100
        n=re.findall(r'\[([^\]]+)\]',mm.group(3))
        s=mm.group(3); w=re.search(r' of (\S+)',s); what=(s.split()[1]+w.group(1)) if w and s.startswith('Pad') else s.split()[0][:5]+s.split(' on ')[-1][:2]
        d[n[0].split('/')[-1] if n else '?'].append('%.2f,%.2f %s'%(x,y,what))
skip=sys.argv[1:] or ['GND','+3V3']
for k,v in sorted(d.items()):
    if k in skip: continue
    print(k,' | '.join(v))
