"""Small leftovers: eFuse split pins (main pad <-> corner pad), switch twin pads."""
from rt import T, V
F = 'F.Cu'
for u, pins in (('U16', ('1', '4', '7', '10')),) + tuple((u, ('1', '4', '7', '10')) for u in ('U10', 'U11', 'U12', 'U13', 'U14')):
    for p in pins:
        a, b = '%s.%s' % (u, p), "%s.%s'" % (u, p)
        from rt import PADS, PADS_NEW
        A, Bp = PADS_NEW[a], PADS_NEW[b]
        def ins(P, bb): return bb[0] <= P[0] <= bb[2] and bb[1] <= P[1] <= bb[3]
        # the two parts touch: one axial leg from a pad centre into the other part, any bend inside pad copper
        if ins((A['x'], Bp['y']), Bp['bb']):
            T(A['net'], 0.2, F, a, '%s@0,%g' % (a, Bp['y'] - A['y']))
        elif ins((Bp['x'], A['y']), A['bb']):
            T(A['net'], 0.2, F, a, '%s@%g,0' % (a, Bp['x'] - A['x']), b)
        else:
            T(A['net'], 0.2, F, a, b)
T('BOOT', 0.2, F, 'SW2.1', "SW2.1'")
T('EN', 0.2, F, 'SW3.1', "SW3.1'")
T('PB_RAW', 0.25, F, 'SW1.1', "SW1.1'")
