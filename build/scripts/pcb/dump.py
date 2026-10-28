# dump.py : pads (ref,num,net,x,y,w,h,rot,layers) + outline + zones -> build/route/board.json (board-local mm, centre 150,100)
import os, sys, json
sys.path.insert(0, os.path.expanduser('~/.claude/skills/layout-placement/scripts'))
from ipc_board import load
b = load(os.path.abspath('E0005_controller.kicad_pcb'))
out = {'fps': [], 'outline': list(b['outline'].exterior.coords)}
for f in b['footprints']:
    d = {'ref': f.ref, 'val': f.value, 'x': f.x-150, 'y': f.y-100, 'rot': f.rot, 'side': 'B' if 'B' in str(f.layer) else 'F', 'pads': []}
    for p in f.pads:
        bx = p.poly.bounds if p.poly is not None else None
        d['pads'].append({'n': p.num, 'net': p.net, 'x': p.center[0]-150, 'y': p.center[1]-100, 'thru': p.through,
                          'bb': [bx[0]-150, bx[1]-100, bx[2]-150, bx[3]-100] if bx else None,
                          'L': [str(l) for l in p.layers] if hasattr(p, 'layers') else None})
    out['fps'].append(d)
os.makedirs('build/route', exist_ok=True)
json.dump(out, open('build/route/board.json', 'w'), indent=0)
print(len(out['fps']), sum(len(f['pads']) for f in out['fps']))
