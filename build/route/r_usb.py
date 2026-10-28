"""USB D+/D- (U1 pins 14/13 <-> R2/R3 series 0R at the USB-C side): 90 ohm edge-coupled microstrip on F.Cu over solid In1 GND.
JLC04161H-3313: L1-L2 prepreg 0.0994 mm, er 4.1.  W = 0.19 mm, S = 0.20 mm (centre pitch 0.39 mm).
The D+ path is drawn by hand; D- is its parallel offset (left of travel, travelling from U1 westwards).
A two-bump accordion on D+ near U1 compensates the D- detour under pin 14 into pin 13."""
import math
from rt import T, V, PADS
F, B = 'F.Cu', 'B.Cu'
W, PITCH = 0.19, 0.39
DP, DN = 'USB_DP', 'USB_DN'

def offset(pts, d):
    """miter offset of a polyline by d to the left of travel (left = +y when travelling -x, y down)."""
    out = []
    n = len(pts)
    def nrm(a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
        return (dy / L, -dx / L)  # left normal in a y-down frame
    for i in range(n):
        if i == 0:
            nx, ny = nrm(pts[0], pts[1]); out.append((pts[0][0] + d * nx, pts[0][1] + d * ny)); continue
        if i == n - 1:
            nx, ny = nrm(pts[-2], pts[-1]); out.append((pts[-1][0] + d * nx, pts[-1][1] + d * ny)); continue
        n1 = nrm(pts[i - 1], pts[i]); n2 = nrm(pts[i], pts[i + 1])
        bx, by = n1[0] + n2[0], n1[1] + n2[1]; bl = math.hypot(bx, by)
        c = (n1[0] * n2[0] + n1[1] * n2[1])
        k = d / math.sqrt((1 + c) / 2)
        out.append((pts[i][0] + k * bx / bl, pts[i][1] + k * by / bl))
    return [(round(x, 4), round(y, 4)) for x, y in out]

Y0 = -8.105            # D+ west run at the module (D- at -7.715, between pin 14 and pin 15)
XD = 29.5              # start of the SW diagonal
Y1 = 6.3               # D+ west run south of the BH2 peg
X2 = -27.0             # start of the NW diagonal (west of the BH2 peg)
Y2 = 4.1               # D+ run into R2.2
# D+ centre line from U1 westwards (with accordion bumps on D+ only, added below)
cl = [(37.7, Y0), (XD, Y0), (XD - (Y1 - Y0), Y1), (X2, Y1), (X2 - (Y1 - Y2), Y2), (-45.6, Y2)]
dn = offset(cl, PITCH)
# D+ : pad 14 -> accordion -> centre line
bump_h, x_b = 0.95, 35.6
acc = [(37.7, Y0), (x_b, Y0), (x_b - bump_h, Y0 - bump_h), (x_b - bump_h - 0.4, Y0 - bump_h), (x_b - 2 * bump_h - 0.4, Y0),
       (x_b - 2 * bump_h - 0.8, Y0), (x_b - 3 * bump_h - 0.8, Y0 - bump_h), (x_b - 3 * bump_h - 1.2, Y0 - bump_h),
       (x_b - 4 * bump_h - 1.2, Y0)]
# third bump on the long run south of the cells (x ~ -12), height chosen so that |len(D+) - len(D-)| <= 0.05 mm
H3 = 1.137; xb3 = -11.0
b3 = [(xb3, Y1), (xb3 - H3, Y1 - H3), (xb3 - H3 - 0.4, Y1 - H3), (xb3 - 2 * H3 - 0.4, Y1)]
dp_pts = [(38.0, Y0)] + acc + cl[1:3] + b3 + cl[3:] + ['R2.2']
T(DP, W, F, *dp_pts)
# D- : pad 13 -> under pin 14 -> offset line -> R3.2
dn_pts = ['U1.13', (39.32, dn[0][1]), (dn[0][0], dn[0][1])] + dn[1:-1] + [(dn[-1][0], dn[-1][1]), (-45.6 - 0.0, 5.1), 'R3.2']
T(DN, W, F, *dn_pts)
# ---------------- USB-C side: J11 A6/A7 straight in, B6/B7 tied with small vias + B.Cu; U4 ESD pass-through; R2.1 / R3.1
DPC, DNC = 'USB_DP_C', 'USB_DN_C'
T(DPC, W, F, 'J11.A6', (-53.0, 4.25), (-52.6, 3.85), (-52.3, 3.55), 'U4.1', 'U4.6', (-48.2, 3.55), (-47.85, 3.9), 'R2.1')
T(DNC, W, F, 'J11.A7', (-53.6, 4.75), (-52.8, 4.75), (-52.35, 5.2), (-51.9, 5.2), 'U4.3', 'U4.4', (-48.2, 5.45), (-47.85, 5.1), 'R3.1')
V(DNC, -53.6, 4.75, dia=0.45, drill=0.3); V(DNC, -53.6, 3.75, dia=0.45, drill=0.3)
V(DPC, -53.0, 4.25, dia=0.45, drill=0.3); V(DPC, -53.0, 5.25, dia=0.45, drill=0.3)
T(DNC, 0.2, F, 'J11.B7', (-53.6, 3.75)); T(DNC, 0.2, B, (-53.6, 3.75), (-53.6, 4.75))
T(DPC, 0.2, F, 'J11.B6', (-53.0, 5.25)); T(DPC, 0.2, B, (-53.0, 5.25), (-53.0, 4.25))
