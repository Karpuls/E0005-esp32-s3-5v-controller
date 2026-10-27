"""E0005 silkscreen pass on the saved board file (adapted from E0003 pcb_silk.py).

Reference designators at 1.0 mm / 0.15 mm (JLC minimum) only where they fit: clear of every pad
(0.25 mm), every footprint silk graphic (0.2 mm), board-level silk text, other references and the
board edge (0.35 mm).  A reference that fits nowhere is hidden (it stays on the Fab layer).
Bottom-side footprints: references hidden (under the cell holders).

Edits only the Reference property of footprints (position / angle / size / hide); the KiCad API
server must not have the board open (stop it, run this, reopen).
Usage: python3 silk.py [board]
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from shapely.affinity import rotate as srot  # noqa: E402
from shapely.geometry import box, Point, LineString, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

import pcb_kpcb as kpcb  # noqa: E402
from pcb_kpcb import OX, OY, load_fp, _copy, _flip_tree, _find, fnum  # noqa: E402
from pcb_sexp import parse, dump, Sym  # noqa: E402

H, TH, CW = 1.0, 0.15, 0.95
PAD_CLR, SILK_CLR, EDGE_CLR, TXT_CLR = 0.25, 0.3, 0.35, 0.25
PRIORITY = ['U1', 'U2', 'U17', 'U16', 'U5', 'U4', 'U6', 'U8', 'U9', 'U15', 'L1', 'L2', 'F1', 'Q1', 'Q2', 'R20', 'R147',
            'J11', 'J1', 'J2', 'J3', 'J4', 'J5', 'J10', 'SW1', 'SW2', 'SW3', 'D1', 'D2', 'D11']


def text_box(cx, cy, s, vertical=False):
    w, h = CW * len(s) + TH, H + TH
    if vertical:
        w, h = h, w
    return box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def arc_pts(s, m, e, n=16):
    (x1, y1), (x2, y2), (x3, y3) = s, m, e
    d = 2 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
    if abs(d) < 1e-9:
        return [s, e]
    ux = ((x1 * x1 + y1 * y1) * (y2 - y3) + (x2 * x2 + y2 * y2) * (y3 - y1) + (x3 * x3 + y3 * y3) * (y1 - y2)) / d
    uy = ((x1 * x1 + y1 * y1) * (x3 - x2) + (x2 * x2 + y2 * y2) * (x1 - x3) + (x3 * x3 + y3 * y3) * (x2 - x1)) / d
    r = math.hypot(x1 - ux, y1 - uy)
    a1, a2, a3 = (math.atan2(p[1] - uy, p[0] - ux) for p in (s, m, e))
    def norm(a):
        return a % (2 * math.pi)
    sweep = norm(a3 - a1)
    if norm(a2 - a1) > sweep:
        sweep -= 2 * math.pi
    return [(ux + r * math.cos(a1 + sweep * k / n), uy + r * math.sin(a1 + sweep * k / n)) for k in range(n + 1)]


def fp_silk(prt):
    src = _copy(load_fp(prt.libid))
    out = []
    lay_want = 'F.SilkS'
    for it in src[2:]:
        if not isinstance(it, list) or it[0] not in ('fp_line', 'fp_rect', 'fp_circle', 'fp_arc', 'fp_poly'):
            continue
        lay = _find(it, 'layer')
        if lay is None or lay[1] != lay_want:
            continue
        g = {}
        for k in ('start', 'end', 'mid', 'center'):
            p = _find(it, k)
            if p is not None:
                g[k] = prt.to_abs(float(p[1]), float(p[2]))
        st = _find(it, 'stroke')
        w = float(_find(st, 'width')[1]) if st is not None else 0.12
        if it[0] == 'fp_line':
            out.append(LineString([g['start'], g['end']]).buffer(w / 2))
        elif it[0] == 'fp_rect':
            corners = []
            s = _find(it, 'start'); e = _find(it, 'end')
            for lx, ly in ((s[1], s[2]), (e[1], s[2]), (e[1], e[2]), (s[1], e[2])):
                corners.append(prt.to_abs(float(lx), float(ly)))
            out.append(Polygon(corners).exterior.buffer(w / 2))
        elif it[0] == 'fp_circle':
            c, e = g['center'], g['end']
            out.append(Point(c).buffer(math.hypot(e[0] - c[0], e[1] - c[1])).exterior.buffer(w / 2))
        elif it[0] == 'fp_arc':
            out.append(LineString(arc_pts(g['start'], g['mid'], g['end'])).buffer(w / 2))
        elif it[0] == 'fp_poly':
            pts = [prt.to_abs(float(p[1]), float(p[2])) for p in _find(it, 'pts')[1:]]
            if len(pts) >= 3:
                out.append(Polygon(pts).buffer(w / 2))
    return out


def pad_geoms(prt):
    out = []
    for p in prt.pads():
        if p['shape'] in ('circle',):
            g = Point(p['cx'], p['cy']).buffer(p['w'] / 2)
        else:
            g = box(p['cx'] - p['w'] / 2, p['cy'] - p['h'] / 2, p['cx'] + p['w'] / 2, p['cy'] + p['h'] / 2)
            g = srot(g, -p['ang'], origin=(p['cx'], p['cy']))
        out.append((g, p))
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else kpcb.BOARD
    t = parse(open(path).read())
    comps, nets = kpcb.load_netlist(os.path.join(kpcb.PROJ, 'build', 'layout', 'current.net'))
    fps = {}
    for fp in t:
        if not (isinstance(fp, list) and fp and fp[0] == 'footprint'):
            continue
        ref = [p for p in fp if isinstance(p, list) and p and p[0] == 'property' and p[1] == 'Reference'][0]
        at = _find(fp, 'at')
        tr = _find(fp, 'transform')
        if at is None and tr is not None:       # KiCad 10.99 footprint transform
            tl, ro = _find(tr, 'translate'), _find(tr, 'rotate')
            at = ['at', tl[1], tl[2], ro[1] if ro is not None else 0]
        side = 'B' if _find(fp, 'layer')[1] == 'B.Cu' else 'F'
        comp = comps.get(ref[2]) or dict(ref=ref[2], value='', footprint=fp[1], tstamp='', fields=[], props={})
        comp = dict(comp, footprint=fp[1])
        prt = kpcb.Part(ref[2], comp, float(at[1]) - OX, float(at[2]) - OY,
                        float(at[3]) if len(at) > 3 else 0.0, side, nets)
        fps[ref[2]] = (fp, ref, prt)

    # obstacles (absolute page coords)
    obst = []
    for r, (fp, prop, prt) in fps.items():
        for g, p in pad_geoms(prt):
            if prt.side == 'F' or p['drill']:
                obst.append(g.buffer(PAD_CLR))
        if prt.side == 'F':
            obst += [g.buffer(SILK_CLR) for g in fp_silk(prt)]
    for it in t:
        if isinstance(it, list) and it and it[0] == 'gr_text' and _find(it, 'layer')[1] == 'F.SilkS':
            at = _find(it, 'at')
            s = it[1]
            vert = len(at) > 3 and abs(float(at[3])) % 180 == 90
            sz = float(_find(_find(_find(it, 'effects'), 'font'), 'size')[1])
            w = CW * sz * len(s) + TH
            h = sz + TH
            if vert:
                w, h = h, w
            obst.append(box(float(at[1]) - w / 2, float(at[2]) - h / 2, float(at[1]) + w / 2,
                            float(at[2]) + h / 2).buffer(TXT_CLR))
    edge = box(OX - 62.5 + EDGE_CLR, OY - 32.5 + EDGE_CLR, OX + 62.5 - EDGE_CLR, OY + 32.5 - EDGE_CLR)
    # antenna keep-out strip: no silk on the antenna area either
    obst.append(box(OX + 56.05, OY - 24, OX + 63, OY + 24))
    U = unary_union(obst)

    order = [r for r in PRIORITY if r in fps] + sorted(r for r in fps if r not in PRIORITY)
    shown = hidden = 0
    for ref in order:
        fp, prop, prt = fps[ref]
        if ref == 'OUT1':
            continue
        if prt.side == 'B':
            set_hidden(prop, True); hidden += 1
            continue
        cy = prt.courtyard()
        x0, y0, x1, y1 = cy if cy else (prt.x + OX - .5, prt.y + OY - .5, prt.x + OX + .5, prt.y + OY + .5)
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        hw = CW * len(ref) / 2 + 0.2
        cands = []
        if (x1 - x0) > 2 * hw + 0.6 and (y1 - y0) > 2.0:
            cands.append((mx, my, False))
        for d in (0.7, 1.0, 1.4):
            cands += [(mx, y0 - d, False), (mx, y1 + d, False), (x0 - hw - d + 0.6, my, False), (x1 + hw + d - 0.6, my, False)]
        for d in (0.7, 1.0):
            cands += [(x0 - d, my, True), (x1 + d, my, True)]
        for d in (0.7, 1.0):     # corners
            cands += [(x0 - hw + 0.4, y0 - d, False), (x1 + hw - 0.4, y0 - d, False),
                      (x0 - hw + 0.4, y1 + d, False), (x1 + hw - 0.4, y1 + d, False)]
        ok = None
        for x, y, vert in cands:
            tb = text_box(x, y, ref, vert)
            if edge.contains(tb) and not U.intersects(tb):
                ok = (x, y, vert)
                break
        if ok is None:
            set_hidden(prop, True); hidden += 1
            continue
        x, y, vert = ok
        U = U.union(text_box(x, y, ref, vert).buffer(TXT_CLR))
        lx, ly = kpcb.rot(x - OX - prt.x, y - OY - prt.y, -prt.a)
        at = _find(prop, 'at')
        at[1:] = [fnum(lx), fnum(ly), fnum(90 if vert else 0)]
        eff = _find(prop, 'effects')
        font = _find(eff, 'font')
        font[1:] = [[Sym('size'), fnum(H), fnum(H)], [Sym('thickness'), fnum(TH)]]
        eff[:] = [e for e in eff if not (isinstance(e, list) and e and e[0] == 'justify')]
        set_hidden(prop, False)
        _find(prop, 'layer')[1] = 'F.SilkS'
        shown += 1
    open(path, 'w').write(dump(t, 0) + '\n')
    print('references shown', shown, 'hidden', hidden)


def set_hidden(prop, hide):
    prop[:] = [x for x in prop if not (isinstance(x, list) and x and x[0] == 'hide')]
    if hide:
        i = [k for k, x in enumerate(prop) if isinstance(x, list) and x and x[0] == 'layer'][0]
        prop.insert(i + 1, [Sym('hide'), Sym('yes')])


if __name__ == '__main__':
    main()
