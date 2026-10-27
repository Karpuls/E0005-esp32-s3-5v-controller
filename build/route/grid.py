# grid.py net x0 y0 x1 y1 [step] : list via spots (0.6/0.3) with >= 0.15 to other-net copper on all layers
import sys
from shapely.geometry import Point
import probe, rt
net = rt.net(sys.argv[1]); x0, y0, x1, y1 = map(float, sys.argv[2:6]); st = float(sys.argv[6]) if len(sys.argv) > 6 else 0.05
res = []
y = y0
while y <= y1 + 1e-9:
    x = x0
    while x <= x1 + 1e-9:
        g = Point(x, y).buffer(0.3); m = 9
        for L in probe.OBS:
            for n, o, w in probe.OBS[L]:
                if n == net and not w.startswith('pad'): continue
                d = g.distance(o)
                if d < m: m = d
        if m >= 0.15: res.append((round(x, 2), round(y, 2), round(m, 2)))
        x += st
    y += st
print(len(res), res[:40])
