"""enlarge.py: grow the board 8 mm to the north (125 x 65 -> 125 x 73).
Everything north of a stepped cut line (x < 33.6) moves north by D: footprints, board texts, the north Edge.Cuts edge.
OUT1 (one 4 x M3 footprint from lib/E0005_mech, not editable) is replaced by E0005_board:Holes_4xM3_125x73 with the same
3.2 / 6.0 mm plated holes 4 mm in from each corner.  Run with the API server stopped.  Tracks/vias/R_* zones are regenerated
by build.py, whose coordinates go through rt.xf() (the same transform)."""
import re, sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from xfm import moved, D, X0, Y0
PCB = os.path.join(HERE, '../../E0005_controller.kicad_pcb')
s = open(PCB).read()
B = json.load(open(os.path.join(HERE, 'board.json')))
MOVE = set()
for f in B['fps']:
    if f['ref'] in ('OUT1', 'BH1', 'BH2'):
        continue
    if moved(f['x'], f['y']):
        MOVE.add(f['ref'])
print(len(MOVE), 'footprints move')
# ---- split top-level blocks
def blocks(s):
    i = 0; out = []
    while True:
        j = s.find('\n\t(', i)
        if j < 0:
            out.append(s[i:]); return out
        out.append(s[i:j + 1]); i = j + 1
# simpler: walk top-level s-expressions starting with "\t(" at depth 1
def toplevel(s):
    res = []; depth = 0; start = None
    k = 0; n = len(s); inq = False
    while k < n:
        c = s[k]
        if inq:
            if c == '\\': k += 2; continue
            if c == '"': inq = False
        elif c == '"': inq = True
        elif c == '(':
            depth += 1
            if depth == 2: start = k
        elif c == ')':
            if depth == 2: res.append((start, k + 1))
            depth -= 1
        k += 1
    return res
spans = toplevel(s)
NDESCR = '(descr "E0005 4 x M3 mounting holes (3.2 mm plated, 6 mm pad) 4 mm from each corner of the 125 x 73 mm outline (E0003 hole footprint with the outline enlarged 8 mm north during E0005 routing); the outline itself is board-level Edge.Cuts. Board-only.")'
def TF(s):
    def f(m):
        y = float(m.group(3))
        if 24 < abs(y) < 35: y = (abs(y) + 4) * (1 if y > 0 else -1)
        return '(%s %s %g' % (m.group(1), m.group(2), y)
    s = re.sub(r'\((center|end|start|mid|at) ([-\d.]+) ([-\d.]+)', f, s)
    return s.replace('E0003 outline 125 x 65', 'E0005 outline 125 x 73')

edits = []
def ref_of(t):
    m = re.search(r'\(property "Reference" "([^"]+)"', t); return m.group(1) if m else None
for a, b in spans:
    t = s[a:b]
    head = t[:30]
    if t.startswith('(footprint'):
        r = ref_of(t)
        if r in MOVE:
            m = re.search(r'\(translate ([-\d.]+) ([-\d.]+)\)', t)
            y = float(m.group(2)) - D
            t2 = t[:m.start(2)] + ('%g' % y) + t[m.end(2):]
            edits.append((a, b, t2))
        elif r == 'OUT1':
            t2 = t.replace('"E0005_mech:E0003_Holes_4xM3"', '"E0005_board:Holes_4xM3_125x73"').replace('"E0003_Holes_4xM3"', '"Holes_4xM3_125x73"')
            t2 = re.sub(r'\(descr "[^"]*"\)', lambda m: NDESCR, t2, count=1)
            m = re.search(r'\(translate ([-\d.]+) ([-\d.]+)\)', t2)
            t2 = t2[:m.start(2)] + ('%g' % (float(m.group(2)) - D / 2)) + t2[m.end(2):]
            t2 = TF(t2)
            edits.append((a, b, t2))
    elif t.startswith('(gr_text'):
        m = re.search(r'\(at ([-\d.]+) ([-\d.]+)', t)
        x, y = float(m.group(1)) - X0, float(m.group(2)) - Y0
        if moved(x, y):
            edits.append((a, b, t[:m.start(2)] + '%g' % (float(m.group(2)) - D) + t[m.end(2):]))
    elif (t.startswith('(gr_line') or t.startswith('(gr_arc')) and '"Edge.Cuts"' in t:
        def f(mm):
            y = float(mm.group(3))
            if y < 75:  # north edge / north corner arcs (KiCad y < 75 = local < -25)
                y -= D
            elif mm.group(1) == 'start' and 'gr_line' in t and y < 80:
                y -= D
            return '(%s %s %g)' % (mm.group(1), mm.group(2), y)
        t2 = re.sub(r'\((start|end|mid) ([-\d.]+) ([-\d.]+)\)', f, t)
        edits.append((a, b, t2))
for a, b, t2 in sorted(edits, reverse=True):
    s = s[:a] + t2 + s[b:]
open(PCB, 'w').write(s)
print('edits', len(edits))
