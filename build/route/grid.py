# grid.py net x0 y0 x1 y1 [step] [dia] : list via spots with >= 0.15 to other-net copper on all layers (pads of any net)
import sys
from shapely.geometry import Point, box
from shapely.strtree import STRtree
import probe, rt
net = rt.net(sys.argv[1]); x0, y0, x1, y1 = map(float, sys.argv[2:6])
st = float(sys.argv[6]) if len(sys.argv) > 6 else 0.05; r = (float(sys.argv[7]) if len(sys.argv) > 7 else 0.6) / 2
win = box(x0 - 1, y0 - 1, x1 + 1, y1 + 1)
obs = [o for L in probe.OBS for n, o, w in probe.OBS[L] if not (n == net and not w.startswith('pad')) and o.intersects(win)]
tree = STRtree(obs)
res = []; y = y0
while y <= y1 + 1e-9:
    x = x0
    while x <= x1 + 1e-9:
        g = Point(x, y).buffer(r, 8)
        if all(obs[i].distance(g) >= 0.15 for i in tree.query(g.buffer(0.15))): res.append((round(x, 2), round(y, 2)))
        x += st
    y += st
print(len(res)); print(' '.join('%g,%g' % p for p in res))
