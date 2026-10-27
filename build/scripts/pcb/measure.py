# measure.py : numbers for the placement review (board-local mm)
import os, sys, math
sys.path.insert(0, os.path.expanduser('~/.claude/skills/layout-placement/scripts'))
from ipc_board import load, by_ref
from shapely.geometry import box, Point
b = load(os.path.abspath('E0005_controller.kicad_pcb')); F = by_ref(b)
O = (150, 100)
def cy(r): return F[r].courtyard
def pad(r, n): return [p for p in F[r].pads if p.num == n][0]
def d(a, c): return a.distance(c)
def L(x0, y0, x1, y1): return box(x0 + 150, y0 + 100, x1 + 150, y1 + 100)
print('1. edges: J11 x=%.1f (west), J1-J5 y=%.1f..%.1f (north), J6-9/J12/SW1/J10 y=%.1f..%.1f' % (
    F['J11'].x - 150, min(F[j].y for j in 'J1 J2 J3 J4 J5'.split()) - 100, max(F[j].y for j in 'J1 J2 J3 J4 J5'.split()) - 100,
    min(F[j].y for j in 'J6 J7 J8 J9 J12 SW1 J10'.split()) - 100, max(F[j].y for j in 'J6 J7 J8 J9 J12 SW1 J10'.split()) - 100))
print('   BH1 (%.2f,%.2f) BH2 (%.2f,%.2f) rot %.0f/%.0f' % (F['BH1'].x - 150, F['BH1'].y - 100, F['BH2'].x - 150, F['BH2'].y - 100, F['BH1'].rot, F['BH2'].rot))
ant = L(56.05, -9.0, 62.05, 9.0)
cans = [L(3 - 35.075, -13.05 - 10.775, 3 + 35.075, -13.05 + 10.775), L(3 - 35.075, 13.05 - 10.775, 3 + 35.075, 13.05 + 10.775)]
print('2. antenna (x 56.05-62.05) to nearest cell can (2D): %.2f mm; to MID lug pads: %.2f mm' % (
    min(d(ant, c) for c in cans), min(d(ant, p.poly) for r in ('BH1', 'BH2') for p in F[r].pads if p.num == '1' and p.center[0] > 180 or p.num == '2' and p.center[0] > 180)))
res = L(-62.0, -31.8, -38.2, -17.6); keep = L(-55.7, -26.6, -38.2, -19.0)
print('3. U_IN reservation 23.8 x 14.2; keep area %.1f x %.1f; clearance to:' % (17.3, 7.6),
      ', '.join('%s %.2f' % (r, d(res, cy(r))) for r in ('U2', 'L2', 'L1', 'U17')))
inside = [r for r in ('U16', 'C65', 'R133', 'R134', 'R135', 'R136', 'R137', 'R138', 'R139', 'R140', 'R141', 'C66', 'C67', 'Q11', 'Q12') if not keep.buffer(0.01).contains(cy(r))]
print('   U16 passives outside keep area:', inside or 'none')
def pp(a, an, b_, bn):
    return d(pad(a, an).poly, pad(b_, bn).poly)
print('4. U17: C73 VIN-gap %.2f / PGND-gap %.2f; C71 %.2f; C72 %.2f; C74 BOOT %.2f; L1.1-SW pin6 %.2f' % (
    pp('C73', '1', 'U17', '8'), pp('C73', '2', 'U17', '9'), pp('C71', '1', 'U17', '8'), pp('C72', '1', 'U17', '8'), pp('C74', '1', 'U17', '7'), pp('L1', '1', 'U17', '6')))
print('   L1+C75/C76 bbox: %.1f x %.1f mm' % tuple((lambda u: (u.bounds[2] - u.bounds[0], u.bounds[3] - u.bounds[1]))(cy('L1').union(cy('C75')).union(cy('C76')))))
print('   FB: R153 %.2f R154 %.2f, FF R155/C79 C79.2-FB %.2f' % (pp('R153', '2', 'U17', '2'), pp('R154', '1', 'U17', '2'), pp('C79', '2', 'U17', '2')))
print('   U2: C69 SNS %.2f C70 SNS %.2f C8 PMID %.2f C9 PMID %.2f C2 VBUS %.2f C18 BAT %.2f L2 SW %.2f C11 BTST %.2f C20 REGN %.2f' % (
    pp('C69', '1', 'U2', '15'), pp('C70', '1', 'U2', '15'), pp('C8', '1', 'U2', '22'), pp('C9', '1', 'U2', '22'), pp('C2', '1', 'U2', '23'),
    pp('C18', '1', 'U2', '13'), pp('L2', '2', 'U2', '18'), pp('C11', '1', 'U2', '12'), pp('C20', '1', 'U2', '11')))
print('   R147 to RT1 %.1f, RT2 %.1f, U15 %.1f, nearest cell can %.1f mm' % (d(cy('R147'), cy('RT1')), d(cy('R147'), cy('RT2')), d(cy('R147'), cy('U15')), min(d(cy('R147'), c) for c in cans)))
print('5. pack path: B_N lug->Q1 %.1f, Q1-Q2 %.1f, Q2-R20 %.1f, F1-CELL2_P lug %.1f, U6-Q1 %.1f; Kelvin U15.2-R20.1 %.2f, U15.4-NT1 %.2f, NT1-R20.2 %.2f' % (
    d([p for p in F['BH1'].pads if p.num == '2'][0].poly, pad('Q1', '1').poly), d(cy('Q1'), cy('Q2')), d(cy('Q2'), cy('R20')),
    d([p for p in F['BH2'].pads if p.num == '1'][0].poly, pad('F1', '1').poly), d(cy('U6'), cy('Q1')),
    pp('U15', '2', 'R20', '1'), pp('U15', '4', 'NT1', '1'), pp('NT1', '2', 'R20', '2')))
for j, u, tv, esd, c in (('J1', 'U10', 'D19', 'D20', 'C48'), ('J2', 'U11', 'D21', 'D22', 'C51'), ('J3', 'U12', 'D23', 'D24', 'C54'),
                         ('J4', 'U13', 'D25', 'D26', 'C57'), ('J5', 'U14', 'D27', 'D28', 'C60')):
    print('6. %s: eFuse %s %.1f, TVS %s %.1f, ESD %s %.1f mm from connector courtyard; %s to %s IN %.2f' % (
        j, u, d(cy(j), cy(u)), tv, d(cy(j), cy(tv)), esd, d(cy(j), cy(esd)), c, u, pp(c, '1', u, '5')))
mux = F['U8']; js = [F[j] for j in 'J1 J2 J3 J4 J5'.split()]
print('   U8 at x %.1f; J1..J5 x %.1f..%.1f (centre %.1f)' % (mux.x - 150, js[0].x - 150, js[-1].x - 150, (js[0].x + js[-1].x) / 2 - 150))
print('7. U4 to J11 %.2f mm; D+/D- J11 -> U1 pins 13/14 straight-line %.1f mm' % (d(cy('U4'), cy('J11')),
      math.dist(pad('J11', 'A6').center, pad('U1', '14').center)))
