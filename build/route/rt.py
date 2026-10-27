"""Hand-routing helpers (no autorouting): every route is a list of waypoints chosen by hand.
Coordinates are board-local mm (board centre = KiCad 150,100), y down.
T(net, w, layer, *pts, bend='d'|'s'): pts are 'REF.PIN' pad centres or (x, y); a step that is not a
multiple of 45 deg is split into a diagonal + straight part ('d' = diagonal first, 's' = straight first).
V(net, x, y): through via 0.6/0.3 (dia/drill keyword args).
Z(net, layer, pts, name, prio=0, conn='full'|'thermal'|'pth', clr=0.2): copper pour polygon.
"""
import json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, 'board.json')))
PADS = {}
for f in B['fps']:
    for p in f['pads']:
        if p['n']:
            k = '%s.%s' % (f['ref'], p['n'])
            while k in PADS:
                k += "'"
            p['ref'] = f['ref']
            PADS[k] = p
FP = {f['ref']: f for f in B['fps']}
NETS = sorted({p['net'] for p in PADS.values() if p['net']})
ITEMS = []
NM = 1e6

def net(n):
    if n in NETS:
        return n
    c = [x for x in NETS if x.split('/')[-1] == n]
    if len(c) != 1:
        raise KeyError('net %r -> %r' % (n, c))
    return c[0]

def q(v):  # snap to 1 nm grid
    return round(v * NM) / NM

def pt(a):
    if isinstance(a, str):
        dx = dy = 0.0
        m = re.match(r'^([^+@]+)(?:@([-\d.]+),([-\d.]+))?$', a)
        p = PADS[m.group(1)]
        if m.group(2):
            dx, dy = float(m.group(2)), float(m.group(3))
        return (q(p['x'] + dx), q(p['y'] + dy))
    return (q(a[0]), q(a[1]))

def padnet(a):
    return PADS[a.split('@')[0]]['net'] if isinstance(a, str) else None

def split45(a, b, bend):
    dx, dy = b[0] - a[0], b[1] - a[1]
    adx, ady = abs(dx), abs(dy)
    if adx < 1e-7 or ady < 1e-7 or abs(adx - ady) < 1e-7:
        return [a, b]
    sx, sy = math.copysign(1, dx), math.copysign(1, dy)
    d = min(adx, ady)
    if bend == 'd':
        m = (q(a[0] + sx * d), q(a[1] + sy * d))
    else:
        m = (q(b[0] - sx * d), q(b[1] - sy * d))
    return [a, m, b]

def T(n, w, layer, *pts, bend='d'):
    n = net(n)
    for a in pts:
        pn = padnet(a)
        if pn is not None and pn != n:
            raise ValueError('pad %s is on %s, not %s' % (a, pn, n))
    P = [pt(a) for a in pts]
    bends = bend if isinstance(bend, (list, tuple)) else [bend] * (len(P) - 1)
    out = [P[0]]
    for i in range(1, len(P)):
        out += split45(out[-1], P[i], bends[i - 1])[1:]
    for a, b in zip(out, out[1:]):
        if a != b:
            ITEMS.append(dict(k='t', net=n, w=w, L=layer, a=a, b=b))
    return out

def V(n, x, y=None, dia=0.6, drill=0.3):
    if y is None:
        x, y = pt(x)
    ITEMS.append(dict(k='v', net=net(n), p=(q(x), q(y)), d=dia, dr=drill))

def VS(n, pts, **kw):
    for p in pts:
        V(n, p[0], p[1], **kw)

def Z(n, layer, pts, name, prio=0, conn='full', clr=0.2, minw=0.2, spoke=0.4):
    ITEMS.append(dict(k='z', net=net(n) if n else None, L=layer, pts=[pt(p) for p in pts], name=name,
                      prio=prio, conn=conn, clr=clr, minw=minw, spoke=spoke))

def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def save(path=os.path.join(HERE, 'items.json')):
    json.dump(ITEMS, open(path, 'w'))
    return path
