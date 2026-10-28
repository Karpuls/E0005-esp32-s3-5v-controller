#!/usr/bin/env python3
"""E0005 rev A gerber review (kicad-gerbers skill): render every layer FROM THE GERBER/DRILL FILES with pygerber,
on one common frame (the Edge.Cuts extent), and measure the fab checks numerically.

Run in a venv with pygerber 2.4.x, numpy, scipy, pillow:
    uv venv /tmp/e5gv/.venv && uv pip install --python /tmp/e5gv/.venv/bin/python "pygerber[pillow]" numpy scipy
    /tmp/e5gv/.venv/bin/python -I build/scripts/gerber_review.py
Writes fab/E0005_revA/docs/gerber_review/*.png and gerber_review.json (numbers quoted in docs/gerber_review.md).
"""
import json, os, re, sys, io
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from pygerber.gerberx3.api.v2 import GerberFile, ColorScheme, PixelFormatEnum, ImageFormatEnum
from pygerber.common.rgba import RGBA

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
FAB = os.path.join(PROJ, 'fab', 'E0005_revA')
G = os.path.join(FAB, 'gerbers')
OUT = os.path.join(FAB, 'docs', 'gerber_review')
P = 'E0005_controller-'
DPMM = 20
FILES = {'F.Cu': 'F_Cu.gtl', 'In1.Cu': 'In1_Cu.g1', 'In2.Cu': 'In2_Cu.g2', 'B.Cu': 'B_Cu.gbl',
         'F.Mask': 'F_Mask.gts', 'B.Mask': 'B_Mask.gbs', 'F.Paste': 'F_Paste.gtp', 'B.Paste': 'B_Paste.gbp',
         'F.Silk': 'F_Silkscreen.gto', 'B.Silk': 'B_Silkscreen.gbo', 'Edge': 'Edge_Cuts.gm1'}
# Antenna keep-out (board rule area E5P_ANTENNA_KEEPOUT, all copper layers), board coords -> gerber y = -y
KEEPOUT = (206.05, -124.0, 212.6, -76.0)
# Port "5V" legends: board text positions, and the port connectors (pos file)
PORTS = {'J1': (116.5, -62.7), 'J2': (131.0, -62.7), 'J3': (145.5, -62.7), 'J4': (160.0, -62.7), 'J5': (174.5, -62.7)}
BW = ColorScheme(background_color=RGBA.from_hex('#000000'), clear_color=RGBA.from_hex('#000000'),
                 solid_color=RGBA.from_hex('#FFFFFF'), clear_region_color=RGBA.from_hex('#000000'),
                 solid_region_color=RGBA.from_hex('#FFFFFF'), debug_1_color=RGBA.from_hex('#FFFFFF'),
                 debug_2_color=RGBA.from_hex('#FFFFFF'))


def render(path):
    pf = GerberFile.from_file(path).parse()
    info = pf.get_info()
    buf = io.BytesIO()
    pf.render_raster(buf, color_scheme=BW, dpmm=DPMM, image_format=ImageFormatEnum.PNG,
                     pixel_format=PixelFormatEnum.RGB)
    img = np.array(Image.open(io.BytesIO(buf.getvalue())).convert('L')) > 127
    return img, (float(info.min_x_mm), float(info.min_y_mm), float(info.max_x_mm), float(info.max_y_mm))


edge_img, EB = render(os.path.join(G, P + FILES['Edge']))
X0, Y0, X1, Y1 = EB
W, H = int(round((X1 - X0) * DPMM)) + 1, int(round((Y1 - Y0) * DPMM)) + 1


def px(x, y):          # gerber mm -> pixel (col, row)
    return int(round((x - X0) * DPMM)), int(round((Y1 - y) * DPMM))


def place(img, bb):    # put a layer render on the common frame
    c = np.zeros((H, W), bool)
    if bb[2] - bb[0] <= 0:      # empty layer (B.Paste)
        return c
    cx, ry = px(bb[0], bb[3])
    h, w = img.shape
    r0, c0 = max(ry, 0), max(cx, 0)
    r1, c1 = min(ry + h, H), min(cx + w, W)
    c[r0:r1, c0:c1] = img[r0 - ry:r1 - ry, c0 - cx:c1 - cx]
    return c


L = {'Edge': place(edge_img, EB)}
for k, f in FILES.items():
    if k != 'Edge':
        L[k] = place(*render(os.path.join(G, P + f)))


def drills(fn):
    tools, hits, cur = {}, [], None
    for ln in open(os.path.join(G, P + fn)):
        ln = ln.strip()
        m = re.match(r'^T(\d+)C([\d.]+)', ln)
        if m: tools[m[1]] = float(m[2]); continue
        m = re.match(r'^T(\d+)$', ln)
        if m: cur = tools[m[1]]; continue
        m = re.match(r'^X([-\d.]+)Y([-\d.]+)(?:G85X([-\d.]+)Y([-\d.]+))?', ln)
        if m: hits.append((cur, float(m[1]), float(m[2]), m[3] is not None))
    return hits


PTH, NPTH = drills('PTH.drl'), drills('NPTH.drl')
R = {}

# Board inside mask (fill the outline)
_im = Image.new('L', (W, H), 0)
ImageDraw.Draw(_im).rounded_rectangle([px(X0 + 0.1, Y1)[0], px(X0, Y1 - 0.1)[1], px(X1 - 0.1, Y0)[0],
                                       px(X1, Y0 + 0.1)[1]], radius=3 * DPMM, fill=255)
inside = np.array(_im) > 0      # board area: the outline rectangle with R3 corners, inside the 0.1 mm line
lab, n = ndimage.label(L['Edge'])
R['outline'] = dict(bbox_mm=[round(X1 - X0 - 0.1, 3), round(Y1 - Y0 - 0.1, 3)], line_width_mm=0.1, edge_pieces=int(n))
# corner radius: distance from the bbox corner to the first outline pixel along the diagonal
cx, ry = px(X0 + 0.05, Y1 - 0.05)
d = 0
while not L['Edge'][ry + d, cx + d]: d += 1
R['outline']['corner_radius_mm'] = round(d / DPMM / (1 - 1 / np.sqrt(2)), 2)

# Drill summary
def summary(h):
    s = {}
    for t, x, y, slot in h:
        k = '%.2f%s' % (t, ' slot' if slot else ''); s[k] = s.get(k, 0) + 1
    return s
R['drill'] = dict(PTH=summary(PTH), NPTH=summary(NPTH),
                  NPTH_hits=[(t, x, y) for t, x, y, _ in NPTH],
                  PTH_large=[(t, x, y) for t, x, y, _ in PTH if t >= 1.0],
                  PTH_slots=[(t, x, y) for t, x, y, s in PTH if s])

# Copper: coverage, keep-out, In1 voids
kx0, ky0 = px(KEEPOUT[0], KEEPOUT[3]); kx1, ky1 = px(KEEPOUT[2], KEEPOUT[1])
ko = np.zeros((H, W), bool); ko[ky0:ky1 + 1, kx0:kx1 + 1] = True; ko &= inside
R['copper'] = {}
for k in ('F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu'):
    R['copper'][k] = dict(coverage_pct=round(100 * (L[k] & inside).sum() / inside.sum(), 1),
                          keepout_copper_px=int((L[k] & ndimage.binary_erosion(ko, iterations=2)).sum()))
# In1: every void (no copper) inside the outline must contain a drill hit (clearance around a through-hole);
# the antenna keep-out is the one allowed large void.
in1_void = inside & ~L['In1.Cu'] & ~ko
lab, n = ndimage.label(in1_void)
hitlab = set()
for t, x, y, _ in PTH + NPTH:
    c, r = px(x, y); rr = int((t / 2 + 1.0) * DPMM)
    win = lab[max(r - rr, 0):r + rr + 1, max(c - rr, 0):c + rr + 1]
    hitlab.update(int(v) for v in np.unique(win) if v)
ring = inside & ~ndimage.binary_erosion(inside, iterations=int(0.4 * DPMM))
hitlab.update(int(v) for v in np.unique(lab[ring]) if v)
sizes = ndimage.sum(in1_void, lab, range(1, n + 1))
orphan = [(int(i + 1), int(s)) for i, s in enumerate(sizes) if (i + 1) not in hitlab and s > 4]
R['In1'] = dict(voids=int(n), voids_at_drill_or_edge=len(hitlab), voids_elsewhere_gt4px=len(orphan),
                orphans=[dict(px=s, at_mm=[round(X0 + ndimage.center_of_mass(lab == i)[1] / DPMM, 2),
                                           round(-(Y1 - ndimage.center_of_mass(lab == i)[0] / DPMM), 2)])
                         for i, s in orphan[:20]])

# Mask: vias tented (no opening at a 0.30 mm via hit unless it sits inside a pad opening = EP thermal via)
def mask_check(mask, cu):
    lab, n = ndimage.label(mask)
    vias = [(x, y) for t, x, y, _ in PTH if abs(t - 0.30) < 1e-3]
    open_at = []
    for x, y in vias:
        c, r = px(x, y)
        if mask[r, c]:
            area = int((lab == lab[r, c]).sum()) / DPMM ** 2
            open_at.append(dict(at=[x, -y], opening_mm2=round(area, 2)))
    # openings with no copper underneath (other than NPTH holes)
    cu_lab = ndimage.sum(cu, lab, range(1, n + 1))
    no_cu = []
    for i, s in enumerate(cu_lab):
        if s == 0:
            cy, cxm = ndimage.center_of_mass(lab == i + 1)
            no_cu.append([round(X0 + cxm / DPMM, 2), round(Y1 - cy / DPMM, 2)])
    # owner rule: via copper (0.6 mm) >= 0.15 mm from any pad (pad = mask opening, pad_to_mask_clearance 0);
    # vias whose centre is inside an opening are reported above (EP thermal vias are exempt)
    near = []
    dist = ndimage.distance_transform_edt(~mask) / DPMM       # mm from each pixel to the nearest opening
    for x, y in vias:
        c, r = px(x, y)
        if mask[r, c]:
            continue
        gap = dist[r, c] - 0.3                                 # 0.6 mm via pad
        if gap < 0.15 - 0.05:                                  # 1 px (0.05 mm) raster tolerance
            near.append(dict(at=[x, -y], gap_mm=round(float(gap), 2)))
    return dict(openings=int(n), vias=len(vias), via_hits_in_opening=open_at, vias_within_0p15_of_pad=near,
                openings_without_copper=no_cu)
R['F.Mask'] = mask_check(L['F.Mask'], L['F.Cu'])
R['B.Mask'] = mask_check(L['B.Mask'], L['B.Cu'])

# Silk on pads: silk pixels inside mask openings (must be 0: soldermask subtracted), silk outside the board
for s, m in (('F.Silk', 'F.Mask'), ('B.Silk', 'B.Mask')):
    ov = L[s] & ndimage.binary_erosion(L[m], iterations=2)
    ol, on = ndimage.label(ov)
    R[s] = dict(on_mask_opening_px=int(ov.sum()), on_mask_opening_blobs=int(on),
                largest_blob_px=int(max(ndimage.sum(ov, ol, range(1, on + 1)), default=0)), outside_board_px=int((L[s] & ~inside).sum()))
# "5V" legends: silk present in a 3 x 4 mm box at each board text position (x, 64.1)
legend = {}
for j, x in (('J1', 122.7), ('J2', 137.2), ('J3', 151.7), ('J4', 166.2), ('J5', 182.15)):
    c0, r0 = px(x - 1.5, -62.0); c1, r1 = px(x + 1.5, -66.2)
    legend[j] = dict(text_at=[x, 64.1], connector_at=[PORTS[j][0], -PORTS[j][1]],
                     silk_px=int(L['F.Silk'][r0:r1, c0:c1].sum()))
R['legend_5V'] = legend
R['paste'] = {k: int(L[k].sum()) for k in ('F.Paste', 'B.Paste')}

# ---------------------------------------------------------------- images
os.makedirs(OUT, exist_ok=True)
def rgb(*layers):
    im = np.zeros((H, W, 3), np.uint8); im[inside] = (18, 18, 18)
    for m, col in layers: im[m] = col
    im[L['Edge']] = (255, 230, 0)
    return im
def save(name, im, crop=None, scale=None):
    img = Image.fromarray(im)
    if crop: img = img.crop(crop)
    if scale: img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)
    img.save(os.path.join(OUT, name), optimize=True)
holes = np.zeros((H, W), bool)
dimg = Image.fromarray(np.zeros((H, W), np.uint8)); dd = ImageDraw.Draw(dimg)
for t, x, y, _ in PTH + NPTH:
    c, r = px(x, y); rr = t / 2 * DPMM
    dd.ellipse([c - rr, r - rr, c + rr, r + rr], fill=255)
holes = np.array(dimg) > 0
CU = (200, 120, 40)
for k, fn in (('F.Cu', 'F_Cu'), ('In1.Cu', 'In1_Cu'), ('In2.Cu', 'In2_Cu'), ('B.Cu', 'B_Cu')):
    im = rgb((L[k], CU), (holes, (0, 0, 0)))
    im[ko & ~L[k]] = (40, 40, 110)          # keep-out shown blue where empty
    im[ko & L[k]] = (255, 0, 0)             # copper in keep-out shown red
    save('gerber_%s.png' % fn, im)
for s, m, cu, fn in (('F.Silk', 'F.Mask', 'F.Cu', 'F'), ('B.Silk', 'B.Mask', 'B.Cu', 'B')):
    im = rgb((L[cu], (70, 50, 25)), (L[m], (230, 190, 90)), (L[s], (255, 255, 255)), (holes, (0, 0, 0)))
    save('gerber_%s_mask_silk.png' % fn, im)
    im = rgb((L[cu], (70, 50, 25)), (L[m], (230, 190, 90)))
    vias = [(x, y) for t, x, y, _ in PTH if abs(t - 0.30) < 1e-3]
    pim = Image.fromarray(im); pd = ImageDraw.Draw(pim)
    for x, y in vias:
        c, r = px(x, y); pd.ellipse([c - 4, r - 4, c + 4, r + 4], outline=(0, 200, 255), width=2)
    pim.save(os.path.join(OUT, 'gerber_%s_mask_vias.png' % fn), optimize=True)
im = rgb((L['F.Paste'], (180, 180, 180)), (L['B.Paste'], (255, 0, 255)))
save('gerber_paste.png', im)
im = rgb()
pim = Image.fromarray(im); pd = ImageDraw.Draw(pim)
for (hl, col) in ((PTH, (60, 220, 60)), (NPTH, (255, 60, 60))):
    for t, x, y, _ in hl:
        c, r = px(x, y); rr = max(t / 2 * DPMM, 2)
        pd.ellipse([c - rr, r - rr, c + rr, r + rr], outline=col, width=2 if t > 1 else 1)
pim.save(os.path.join(OUT, 'gerber_drill.png'), optimize=True)
# Close-ups: port legends (north band), antenna (east edge), J11 slots (west edge)
for name, (xa, ya, xb, yb) in {'zoom_ports_5V': (110, -60.5, 190, -70), 'zoom_antenna': (190, -74, 212.6, -126),
                               'zoom_J11': (87.5, -96, 100, -113)}.items():
    c0, r0 = px(xa, ya); c1, r1 = px(xb, yb)
    if name == 'zoom_ports_5V':
        im = rgb((L['F.Cu'], (70, 50, 25)), (L['F.Mask'], (230, 190, 90)), (L['F.Silk'], (255, 255, 255)))
    elif name == 'zoom_antenna':
        im = rgb((L['F.Cu'] | L['In1.Cu'] | L['In2.Cu'] | L['B.Cu'], CU), (holes, (0, 0, 0)))
        im[ko & ~(L['F.Cu'] | L['In1.Cu'] | L['In2.Cu'] | L['B.Cu'])] = (40, 40, 110)
        im[L['F.Silk']] = (255, 255, 255)
    else:
        im = rgb((L['F.Cu'], CU), (holes, (0, 0, 0)))
    save('gerber_%s.png' % name, im, crop=(c0, r0, c1, r1), scale=2 if name != 'zoom_antenna' else 1)
json.dump(R, open(os.path.join(OUT, 'gerber_review.json'), 'w'), indent=1)
print(json.dumps({k: v for k, v in R.items() if k not in ('drill',)}, indent=1)[:6000])
print(json.dumps(R['drill'], indent=None))
