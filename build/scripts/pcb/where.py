# where.py [refs...] : footprint positions (board-local, centre 150,100) from the IPC server
import os, sys
sys.path.insert(0, os.path.expanduser('~/.claude/skills/layout-placement/scripts'))
from ipc_board import load
b = load(os.path.abspath('E0005_controller.kicad_pcb'))
want = set(sys.argv[1:])
for f in sorted(b['footprints'], key=lambda f: f.ref):
    if want and f.ref not in want and not any(f.ref.startswith(w.rstrip('*')) and w.endswith('*') for w in want):
        continue
    bb = f.courtyard.bounds if f.courtyard is not None else None
    print('%-5s %7.2f %7.2f %6.1f %s %s' % (f.ref, f.x - 150, f.y - 100, f.rot, 'B' if 'B' in str(f.layer) else 'F',
          '' if bb is None else 'cy[%.1f %.1f %.1f %.1f]' % (bb[0]-150, bb[1]-100, bb[2]-150, bb[3]-100)))
