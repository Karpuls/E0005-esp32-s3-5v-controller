"""stitch.py : candidate GND stitching vias on a grid (clearance-checked against items/pads, outside non-GND F/B/In2 zones,
antenna keep-out and board edge) -> stitch.json"""
import json, sys
sys.argv = ['x']
import rt; rt.NEWFRAME = True
import probe
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
items = json.load(open('items.json'))
bad = []
for it in items:
    if it['k'] == 'z' and it['net'] and it['net'] != 'GND' and it['L'] in ('F.Cu', 'B.Cu') and it['name'] not in ('R_3V3_IN2', 'R_V5_IN2'):
        bad.append(Polygon(it['pts']).buffer(0.6))
    if it['k'] == 'z' and it['L'] == 'In2.Cu' and it['name'] not in ('R_3V3_IN2', 'R_V5_IN2'):
        bad.append(Polygon(it['pts']).buffer(0.6))
bad.append(Polygon([(52.0, -41), (63, -41), (63, -16.0), (52.0, -16.0)]))   # antenna end of U1 (keep clear)
BAD = unary_union(bad)
holes = [(-58.5, -36.5), (58.5, -36.5), (-58.5, 28.5), (58.5, 28.5)]
def ok(x, y):
    p = Point(x, y)
    if BAD.contains(p) or abs(x) > 61.3 or y < -39.3 or y > 31.3: return False
    if any(Point(h).distance(p) < 4.0 for h in holes): return False
    g = p.buffer(0.3)
    for L in probe.OBS:
        for n, geo, what in probe.OBS[L]:
            if g.distance(geo) < (0.25 if n != 'GND' else 0.25):
                return False
    return True
step = float(sys.argv[1]) if len(sys.argv) > 1 else 4.0
out = []
y = -39.0
while y <= 31.0:
    x = -61.0
    while x <= 61.0:
        if ok(x, y): out.append((round(x, 2), round(y, 2)))
        x += step
    y += step
json.dump(out, open('stitch.json', 'w'))
print(len(out))
