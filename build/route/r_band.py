"""Routes through the band opened by the 8 mm north enlargement (new frame: coordinates are final, rt.NEWFRAME = True).
U9 west via column: P1/P2/P4_OFF use B columns x 9.4..10.2 and turn west on B lanes (western column -> southern lane);
PORT5_OFF takes the eastmost B column (x 13.0) and runs east in the band; CHG_CD / USB_ILIM leave U9 east on F under the body
and go up into the band on F.  EXP_INT_N runs on In2 along y -17.95 to the U1 side."""
import rt
rt.NEWFRAME = True
from rt import T, V, Z, rect
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
G = 'GND'
# B columns -> band lanes (west)
T('PORT1_OFF', 0.15, B, (8.75, -15.125), (9.4, -15.125), (9.4, -17.9), (8.0, -17.9))
T('PORT2_OFF', 0.15, B, (7.95, -14.475), (9.8, -14.475), (9.8, -18.3), (8.0, -18.3))
T('PORT4_OFF', 0.15, B, (7.95, -13.175), (10.2, -13.175), (10.2, -18.7), (8.0, -18.7))
# CHG_CD / USB_ILIM: F east from the pins under the U9 body, north out of the body top into the band, F lanes west
for pin, xc, yl in (('U9.9', 12.2, -17.9), ('U9.10', 12.6, -18.3), ('U9.11', 13.0, -18.7)):
    p = rt.PADS_NEW[pin]
    T(p['net'], 0.15, F, (10.6, p['y']), (xc, p['y']), (xc, yl), (8.0, yl))
# PORT5_OFF: eastmost B column, east in the band, via near Q7, F into Q7.1
T('PORT5_OFF', 0.15, B, (8.75, -12.525), (13.0, -12.525), (13.0, -20.5), (21.2, -20.5), (21.2, -27.1)); V('PORT5_OFF', 21.2, -27.1)
T('PORT5_OFF', 0.15, F, (21.2, -27.1), 'Q7.1')
# EXP_INT_N: U9.1 via -> In2 east along y -17.28 -> In2 col x 35.6 south to the U1.25 via
T('EXP_INT_N', 0.15, I2, (8.75, -17.28), (9.07, -17.6), (35.6, -17.6), (35.6, 5.71))   # In2 3V3 strip under the V5 band edge
# EXP_INT_N from the R40.2 via (B) north between the CC sense vias, west to the In2 column
T('EXP_INT_N', 0.15, B, (47.575, -11.5), (47.575, -17.25), (35.6, -17.25)); V('EXP_INT_N', 35.6, -17.25)
# PORT2_EN link to Q4.3 on B (was an In2 column through the V5 band)
T('PORT2_EN', 0.15, B, (-16.3, -17.3), (-16.0, -17.6), (-12.2, -17.6), (-12.2, -30.35), (-11.6, -30.95))
# C57.1 (port-4 input bulk cap) V5 via right below the pad, inside the In2 V5 band
T('V5', 0.4, F, 'C57.1', (19.8, -25.3)); V('V5', 19.8, -25.3)
