"""U8 PCA9548 mux and U9 TCA9535 expander: fan-out (via columns under the TSSOP bodies), pull-ups, decoupling.
Long runs (ports, west power stage, U1) are in r_long.py."""
from rt import T, V, VS, Z, rect, PADS, FP
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
G = 'GND'
def P(k):
    p = PADS[k]; return (p['x'], p['y'])
def pv(pin, v, w=0.15, net=None):
    """pin -> straight stub at the pin's y -> via"""
    p = P(pin); n = net or PADS[pin]['net']
    T(n, w, F, pin, (v[0], p[1])); V(n, v[0], p[1])
    return (v[0], p[1])
# ======================= U9 TCA9535
L1, L2 = 8.75, 7.95
for pin, x in (('U9.4', L1), ('U9.5', L2), ('U9.7', L2), ('U9.8', L1)):   # U9.9-.11 leave under the body (r_band)
    pv(pin, (x, 0))
T('EXP_INT_N', 0.15, F, 'U9.1', (8.95, -17.08), (8.75, -17.28)); V('EXP_INT_N', 8.75, -17.28)
T('PORT3_OFF', 0.15, F, 'U9.6', (5.5, -13.83), (5.5, -15.0), (5.15, -15.35))
T(G, 0.25, F, 'U9.2', (11.6, -16.42), (11.6, -15.78), 'U9.3'); V(G, 11.6, -16.1)
T(G, 0.25, F, 'U9.12', (11.6, -9.92)); V(G, 11.6, -9.92)
T(G, 0.25, F, 'U9.21', (14.45, -15.12)); V(G, 14.45, -15.12)
pv('U9.22', (13.65, 0)); pv('U9.23', (14.45, 0)); pv('U9.17', (14.45, 0))
# U9.13-.16 (PORT1-4_FLT_N): F east to columns into the band (r_band)
T('USBIN_FLT_N', 0.15, F, 'U9.18', (16.95, -13.17), (17.24, -12.88))
T('CHG_PG_N', 0.15, F, 'U9.19', (16.95, -13.83), (17.24, -14.12))
T('BUCK_PG', 0.15, F, 'U9.20', (16.85, -14.48), (16.85, -15.0), (17.1, -15.25), 'R93.2')   # hugs U9: CHG_PG_N leaves R92.2 north
T('+3V3', 0.2, F, 'U9.24', (17.0, -17.08), (17.4, -16.68), (17.4, -16.4))
T('+3V3', 0.2, F, 'C45.1', (16.8, -17.3), (16.6, -17.1))
T('+3V3', 0.2, F, 'R92.1', (19.35, -14.12)); V('+3V3', 19.35, -14.12)   # own via (CHG_PG_N passes north of R92)
T('+3V3', 0.2, F, 'R93.1', (18.6, -16.27), (18.6, -16.6)); V('+3V3', 18.6, -16.6)
T('+3V3', 0.2, F, 'R90.1', (19.35, -12.88)); V('+3V3', 19.35, -12.88)   # own via: USBIN_FLT_N passes between R90 and R92
import rt; rt.NEWFRAME = True   # C45 did not move with the enlargement: via in the final frame
T(G, 0.25, F, 'C45.2', (18.6, -18.37)); V(G, 18.6, -18.37)
rt.NEWFRAME = False
# ======================= U8 PCA9548
CA, CB, CC, CD = -4.45, -3.55, -1.55, -2.45
for pin, x in (('U8.3', CB), ('U8.4', CA), ('U8.6', CA), ('U8.7', CB), ('U8.8', CA), ('U8.9', CB),
               ('U8.10', CA), ('U8.11', CB)):
    pv(pin, (x, 0))
T(G, 0.25, F, 'U8.1', (-4.75, -17.08), (-4.45, -16.78), (-4.45, -16.75)); T(G, 0.25, F, 'U8.2', (-4.75, -16.42), (-4.45, -16.72))
V(G, -4.45, -16.75)
T(G, 0.25, F, 'U8.12', (-7.3, -9.92)); V(G, -7.3, -9.92)
T('PORT1_SDA', 0.15, F, 'U8.4', (-7.0, -15.12), (-7.25, -14.87), 'R64.2')
T('PORT1_SCL', 0.15, F, 'U8.5', (-7.0, -14.48), 'R65.2')
for pin, x in (('U8.13', CC), ('U8.14', CD), ('U8.15', CC), ('U8.18', CD), ('U8.19', CC),
               ('U8.20', CD), ('U8.22', CD), ('U8.23', CC)):
    pv(pin, (x, 0))
y21 = P('U8.21')[1]
T(G, 0.25, F, 'U8.21', (CC, y21)); V(G, CC, y21)
T(G, 0.25, F, (0.3, y21), (1.0, y21), 'C44.2')
T('+3V3', 0.25, F, 'U8.24', (1.1, -17.08), (1.5, -16.68), 'C44.1')
T('I2C1_SDA', 0.15, F, 'R62.2', (2.65, -16.45)); V('I2C1_SDA', 2.65, -16.45)
# U8 right-side pull-ups
T('MUX6_SDA', 0.15, F, 'U8.17', (3.0, -12.53), (3.28, -12.25), 'R76.2@0,-0.12')
T('PORT5_SDA', 0.15, F, (-0.46, -9.8), 'R72.2')
T('PORT5_SCL', 0.15, F, 'U8.14', (1.0, -10.58), (1.25, -10.33))
T('LCD_SCL', 0.15, F, 'U8.16', (2.1, -11.88), (2.45, -11.53), (2.45, -10.2))
