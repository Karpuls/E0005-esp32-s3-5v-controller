"""Small leftovers: eFuse split pins (main pad <-> corner pad), switch twin pads."""
from rt import T, V
F = 'F.Cu'
for u, pins in (('U16', ('1', '4', '10')), ('U10', ('1', '4')), ('U11', ('1', '4')), ('U12', ('1', '4')), ('U13', ('1', '4')), ('U14', ('1', '4'))):
    for p in pins:
        a, b = '%s.%s' % (u, p), "%s.%s'" % (u, p)
        from rt import PADS
        T(PADS[a]['net'], 0.2, F, a, b, bend='s' if a == 'U16.10' else 'd')
T('BOOT', 0.2, F, 'SW2.1', "SW2.1'")
T('EN', 0.2, F, 'SW3.1', "SW3.1'")
T('PB_RAW', 0.25, F, 'SW1.1', "SW1.1'")
