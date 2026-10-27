# rings.py [refs] : clearance of F-side courtyards to the BH1/BH2 top-side keep-out rings (board-local mm)
import os, sys
sys.path.insert(0, os.path.expanduser('~/.claude/skills/layout-placement/scripts'))
from ipc_board import load
from shapely.geometry import Point
from shapely.ops import unary_union
RINGS = [(-35.15, -13.05, 2.4), (-35.15, 13.05, 2.4), (41.15, -13.05, 2.4), (41.15, 13.05, 2.4),
         (-24.6, -22.05, 2.3), (30.6, -4.05, 2.3), (-24.6, 4.05, 2.3), (30.6, 22.05, 2.3),
         (41.15, -22.05, 1.7), (-35.15, 22.05, 1.7)]
R = unary_union([Point(x + 150, y + 100).buffer(r, 64) for x, y, r in RINGS])
b = load(os.path.abspath('E0005_controller.kicad_pcb'))
want = set(sys.argv[1:])
for f in b['footprints']:
    if f.layer != 'F.Cu' or f.courtyard is None or (want and f.ref not in want):
        continue
    d = f.courtyard.distance(R)
    if want or d < 0.05:
        print('%-5s %6.2f %6.2f  ring gap %.2f' % (f.ref, f.x - 150, f.y - 100, d if not f.courtyard.intersects(R) else -f.courtyard.intersection(R).area))
