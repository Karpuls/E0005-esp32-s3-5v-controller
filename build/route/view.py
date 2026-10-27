"""view.py x0 y0 x1 y1 out.png [layers=F,B,2,1] : planning plot of pads (net labels) + items.json routes."""
import json, sys, os, hashlib
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon as MP
HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, 'board.json')))
I = json.load(open(os.path.join(HERE, 'items.json'))) if os.path.exists(os.path.join(HERE, 'items.json')) else []
x0, y0, x1, y1 = map(float, sys.argv[1:5]); out = sys.argv[5]
show = sys.argv[6].split(',') if len(sys.argv) > 6 else ['F', 'B', '2', '1']
LC = {'F.Cu': '#d03030', 'B.Cu': '#3060e0', 'In2.Cu': '#d0a000', 'In1.Cu': '#30a030'}
LK = {'F.Cu': 'F', 'B.Cu': 'B', 'In2.Cu': '2', 'In1.Cu': '1'}
sc = max(x1 - x0, y1 - y0)
fig, ax = plt.subplots(figsize=(16, 16 * (y1 - y0) / (x1 - x0) + 0.5), dpi=110)
ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.set_aspect('equal')
step = 1 if sc < 30 else 2 if sc < 60 else 5
import numpy as np
ax.set_xticks(np.arange(round(x0), x1, step)); ax.set_yticks(np.arange(round(y0), y1, step))
ax.grid(True, lw=0.3, color='#bbb'); ax.tick_params(labelsize=6)
def col(n):
    h = int(hashlib.md5((n or '').encode()).hexdigest()[:6], 16)
    return '#%06x' % (h | 0x404040)
fs = max(3, min(7, 120 / sc))
for z in I:
    if z['k'] == 'z' and LK[z['L']] in show:
        ax.add_patch(MP(z['pts'], closed=True, fc=LC[z['L']], alpha=0.12, ec=LC[z['L']], lw=0.8, ls='--'))
        cx = sum(p[0] for p in z['pts']) / len(z['pts']); cy = sum(p[1] for p in z['pts']) / len(z['pts'])
        if x0 < cx < x1 and y0 < cy < y1: ax.text(cx, cy, z['name'], fontsize=fs, color=LC[z['L']], ha='center')
for f in B['fps']:
    for p in f['pads']:
        if not p['bb']: continue
        bx = p['bb']
        if bx[2] < x0 or bx[0] > x1 or bx[3] < y0 or bx[1] > y1: continue
        if f['side'] == 'B' and not p['thru'] and 'B' not in show: continue
        c = 'gray' if not p['net'] else ('#2a8a2a' if p['net'] == 'GND' else col(p['net']))
        ax.add_patch(Rectangle((bx[0], bx[1]), bx[2] - bx[0], bx[3] - bx[1], fc=c, alpha=0.55 if f['side'] == 'F' or p['thru'] else 0.25, ec='k', lw=0.3))
        lab = '%s.%s\n%s' % (f['ref'], p['n'], (p['net'] or '').split('/')[-1][:12])
        ax.text(p['x'], p['y'], lab, fontsize=fs * 0.75, ha='center', va='center', clip_on=True)
for t in I:
    if t['k'] == 't' and LK[t['L']] in show:
        ax.plot([t['a'][0], t['b'][0]], [t['a'][1], t['b'][1]], color=LC[t['L']], lw=max(0.6, t['w'] * 72 * 16 / sc / 25.4 * 0.9), alpha=0.6, solid_capstyle='round')
    if t['k'] == 'v':
        ax.add_patch(Circle(t['p'], t['d'] / 2, fc='#888', ec='k', lw=0.4, alpha=0.9))
fig.savefig(out, bbox_inches='tight'); print(out)
