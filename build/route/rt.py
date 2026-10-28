"""Hand-routing helpers (no autorouting): every route is a list of waypoints chosen by hand.
Coordinates are board-local mm (board centre = KiCad 150,100), y down.
T(net, w, layer, *pts, bend='d'|'s'): pts are 'REF.PIN' pad centres or (x, y); a step that is not a
multiple of 45 deg is split into a diagonal + straight part ('d' = diagonal first, 's' = straight first).
V(net, x, y): through via 0.6/0.3 (dia/drill keyword args).
Z(net, layer, pts, name, prio=0, conn='full'|'thermal'|'pth', clr=0.2): copper pour polygon.
"""
import json, math, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
import copy
from xfm import D as _D
B = json.load(open(os.path.join(HERE, 'board.json')))          # current board (after the 8 mm north enlargement)
_MV = set(json.load(open(os.path.join(HERE, 'moved_refs.json'))))
def _pads(b, old):
    P = {}
    for f in b['fps']:
        for p in f['pads']:
            if p['n']:
                k = '%s.%s' % (f['ref'], p['n'])
                while k in P:
                    k += "'"
                p = dict(p); p['ref'] = f['ref']
                if old and f['ref'] in _MV:
                    p['y'] += _D; p['bb'] = [p['bb'][0], p['bb'][1] + _D, p['bb'][2], p['bb'][3] + _D] if p['bb'] else None
                P[k] = p
    return P
PADS = _pads(B, True)        # route modules work in the pre-enlargement frame; output goes through xfm.xf once
PADS_NEW = _pads(B, False)   # current frame (probe / grid / view tools)
FP = {f['ref']: (dict(f, y=f['y'] + _D) if f['ref'] in _MV else f) for f in B['fps']}   # old frame like PADS
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

NEWFRAME = False   # modules written after the 8 mm north enlargement set rt.NEWFRAME = True (coordinates already final)
from xfm import xf as _xf
def _X(p):
    return p if NEWFRAME else _xf(p)
def ptx(a):
    """output-frame point: pads always via xf (old pad -> current pad); tuples via xf unless NEWFRAME"""
    if isinstance(a, str):        # pads: current position (+ offset), never transformed
        m = re.match(r'^([^+@]+)(?:@([-\d.]+),([-\d.]+))?$', a)
        p = PADS_NEW[m.group(1)]
        dx, dy = (float(m.group(2)), float(m.group(3))) if m.group(2) else (0.0, 0.0)
        return (q(p['x'] + dx), q(p['y'] + dy))
    p = pt(a)
    if not NEWFRAME:
        p = _xf(p)
    return (q(p[0]), q(p[1]))

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

def split3(a, b):
    """pad-to-pad leg: straight half, 45-degree middle, straight half (square exits from both pads)"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    adx, ady = abs(dx), abs(dy)
    if adx < 1e-7 or ady < 1e-7 or abs(adx - ady) < 1e-7:
        return [a, b]
    sx, sy = math.copysign(1, dx), math.copysign(1, dy)
    d = min(adx, ady)
    if adx > ady:
        m1 = (q(a[0] + sx * (adx - d) / 2), a[1]); m2 = (q(m1[0] + sx * d), b[1])
    else:
        m1 = (a[0], q(a[1] + sy * (ady - d) / 2)); m2 = (b[0], q(m1[1] + sy * d))
    return [a, m1, m2, b]

def T(n, w, layer, *pts, bend=None):
    n = net(n)
    for a in pts:
        pn = padnet(a)
        if pn is not None and pn != n:
            raise ValueError('pad %s is on %s, not %s' % (a, pn, n))
    P = [ptx(a) for a in pts]
    ispad = [isinstance(a, str) for a in pts]
    # a pad leg that is off-axis by < 0.05 mm (pad-centre decimals): slide the pad end so the leg is truly axial
    for i in range(len(P) - 1):
        for pi, oi in ((i, i + 1), (i + 1, i)):
            if ispad[pi] and not ispad[oi]:
                dx, dy = P[oi][0] - P[pi][0], P[oi][1] - P[pi][1]
                if 1e-6 < abs(dx) < 0.05 and abs(dy) > 0.1: P[pi] = (P[oi][0], P[pi][1])
                elif 1e-6 < abs(dy) < 0.05 and abs(dx) > 0.1: P[pi] = (P[pi][0], P[oi][1])
    if bend is None:   # square pad exits: legs leave a pad straight first and enter a pad straight last
        bends = ['3' if ispad[i] and ispad[i + 1] else ('s' if ispad[i] else 'd') for i in range(len(P) - 1)]
    else:
        bends = bend if isinstance(bend, (list, tuple)) else [bend] * (len(P) - 1)
    out = [P[0]]
    for i in range(1, len(P)):
        out += (split3(out[-1], P[i]) if bends[i - 1] == '3' else split45(out[-1], P[i], bends[i - 1]))[1:]
    for a, b in zip(out, out[1:]):
        if a != b:
            ITEMS.append(dict(k='t', net=n, w=w, L=layer, a=a, b=b))
    return out

def V(n, x, y=None, dia=0.6, drill=0.3):
    if y is None:
        x, y = ptx(x)
    else:
        x, y = _X((x, y))
    ITEMS.append(dict(k='v', net=net(n), p=(q(x), q(y)), d=dia, dr=drill))

def VS(n, pts, **kw):
    for p in pts:
        V(n, p[0], p[1], **kw)

def Z(n, layer, pts, name, prio=0, conn='full', clr=0.2, minw=0.2, spoke=0.4):
    ITEMS.append(dict(k='z', net=net(n) if n else None, L=layer, pts=[ptx(p) for p in pts], name=name,
                      prio=prio, conn=conn, clr=clr, minw=minw, spoke=spoke))

def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]

def save(path=os.path.join(HERE, 'items.json')):
    json.dump(ITEMS, open(path, 'w'))
    return path
