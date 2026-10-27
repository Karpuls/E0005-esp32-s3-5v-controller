"""probe.py : clearance check of candidate items (hand-drawn) against the current items + pads.
usage in python: from probe import check; check(net, layer, pts, w) / check_via(net, x, y)"""
import json, os
from shapely.geometry import LineString, Point, box
from shapely.affinity import rotate
import rt
HERE = os.path.dirname(os.path.abspath(__file__))
OBS = {'F.Cu': [], 'B.Cu': [], 'In2.Cu': [], 'In1.Cu': []}
def _load():
    for k, p in rt.PADS_NEW.items():
        b = p['bb']; g = box(*b)
        Ls = ['F.Cu', 'B.Cu', 'In2.Cu', 'In1.Cu'] if p['thru'] else [l for l in (p['L'] or []) if l in OBS]
        for L in Ls:
            OBS[L].append((p['net'], g, 'pad ' + k))
    for it in json.load(open(os.path.join(HERE, 'items.json'))):
        if it['k'] == 't':
            OBS[it['L']].append((it['net'], LineString([it['a'], it['b']]).buffer(it['w'] / 2), 'trk'))
        elif it['k'] == 'v':
            for L in OBS:
                OBS[L].append((it['net'], Point(it['p']).buffer(it['d'] / 2), 'via'))
_load()
def _rep(net, geo, layers, tag, pads_any=False):
    net = rt.net(net); worst = []
    for L in layers:
        for n, g, what in OBS[L]:
            if n == net and not (pads_any and what.startswith('pad')): continue
            d = geo.distance(g)
            if d < 0.2:
                worst.append((round(d, 3), L, what, (n or '').split('/')[-1]))
    worst.sort()
    print(tag, 'OK' if not worst or worst[0][0] >= 0.15 else 'CLASH', worst[:4])
def check(net, layer, pts, w=0.15):
    P = [rt.pt(p) for p in pts]
    _rep(net, LineString(P).buffer(w / 2), [layer], '%s %s' % (net, layer))
def check_via(net, x, y, d=0.6):
    _rep(net, Point(x, y).buffer(d / 2), list(OBS), 'via %s (%.2f,%.2f)' % (net, x, y), True)
