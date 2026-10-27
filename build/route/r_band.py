"""Routes through the band opened by the 8 mm north enlargement (new frame: coordinates are final, rt.NEWFRAME = True).
U9 west via column: P1/P2/P4_OFF use B columns x 9.4..10.2 and turn west on B lanes (western column -> southern lane);
PORT5_OFF takes the eastmost B column (x 13.0) and runs east in the band; CHG_CD / USB_ILIM leave U9 east on F under the body
and go up into the band on F.  EXP_INT_N runs on In2 along y -17.95 to the U1 side."""
import rt
rt.NEWFRAME = True
from rt import T, V, Z, rect
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
G = 'GND'
# P1/P2/P4_OFF: B columns x 9.4/9.8/10.2 -> short B lanes -> vias east of the x 7.6 3V3 riser -> F lanes west
T('PORT1_OFF', 0.15, B, (8.75, -15.125), (9.4, -15.125), (9.4, -19.3), (8.6, -19.3)); V('PORT1_OFF', 8.6, -19.3)
T('PORT2_OFF', 0.15, B, (7.95, -14.475), (9.8, -14.475), (9.8, -20.1), (8.2, -20.1)); V('PORT2_OFF', 8.2, -20.1)
T('PORT4_OFF', 0.15, B, (7.95, -13.175), (10.2, -13.175), (10.2, -20.9), (8.6, -20.9)); V('PORT4_OFF', 8.6, -20.9)
# PORT1_OFF: F lane y -19.3 west, R80.2 (pull-up, below the band) and Q3.1 (east of the BH1 peg)
T('PORT1_OFF', 0.15, F, (8.6, -19.3), (-22.64, -19.3)); V('PORT1_OFF', -22.64, -19.3)
T('PORT1_OFF', 0.15, B, (-22.64, -19.3), (-23.4, -18.54), (-23.4, -16.99)); V('PORT1_OFF', -23.4, -16.99)
T('PORT1_OFF', 0.15, F, (-23.4, -16.99), 'R80.2')
T('PORT1_OFF', 0.15, F, (-22.3, -19.3), (-22.3, -24.4), (-23.2, -25.3), 'Q3.1')
# PORT2_OFF: F lane y -20.1 west, north at x -7.6 into Q4.1
T('PORT2_OFF', 0.15, F, (8.2, -20.1), (-8.8, -20.1), 'R82.2')
# PORT4_OFF: F lane y -20.9 -> via -> B col x 4.0 -> via -> F into Q6.1 (west side)
T('PORT4_OFF', 0.15, F, (8.6, -20.9), (4.3, -20.9)); V('PORT4_OFF', 4.3, -20.9)
T('PORT4_OFF', 0.15, B, (4.3, -20.9), (4.0, -21.2), (4.0, -30.15), (4.4, -30.55)); V('PORT4_OFF', 4.4, -30.55)
T('PORT4_OFF', 0.15, F, (4.4, -30.55), (5.4, -30.55))
# PORT3_OFF: Q5.1 -> via -> B across the band -> via -> F to R84.2 (keeps F free for the west lanes)
T('PORT3_OFF', 0.15, F, 'Q5.1', (5.6, -24.2)); V('PORT3_OFF', 5.6, -24.2)
T('PORT3_OFF', 0.15, B, (5.6, -24.2), (5.6, -16.9)); V('PORT3_OFF', 5.6, -16.9)
T('PORT3_OFF', 0.15, F, (5.6, -16.9), 'R84.2')
# CHG_CD / USB_ILIM: F east from the pins under the U9 body, north out of the body top into the band, F lanes west
for pin, xc, yl in (('U9.10', 12.6, -17.9), ('U9.11', 13.0, -18.5)):
    p = rt.PADS_NEW[pin]
    T(p['net'], 0.15, F, (10.6, p['y']), (xc, p['y']), (xc, yl), (8.0, yl))
# CHG_CD: U9.9 -> F stub -> via (7.95,-11.875) -> In2 column x 6.2 (3V3 plane) south -> joins the U2 bundle in the centre (r_bundle)
T('CHG_CD', 0.15, F, 'U9.9', (7.95, -11.875)); V('CHG_CD', 7.95, -11.875)
# PORT5_OFF: eastmost B column, east in the band, via near Q7, F into Q7.1
T('PORT5_OFF', 0.15, B, (8.75, -12.525), (13.0, -12.525), (13.0, -20.5), (21.2, -20.5), (21.2, -27.1)); V('PORT5_OFF', 21.2, -27.1)
T('PORT5_OFF', 0.15, F, (21.2, -27.1), 'Q7.1')
# EXP_INT_N: U9.1 via -> In2 east along y -17.28 -> In2 col x 35.6 south to the U1.25 via
T('EXP_INT_N', 0.15, I2, (8.75, -17.28), (9.07, -17.6), (35.6, -17.6), (35.6, 5.71))   # In2 3V3 strip under the V5 band edge
# EXP_INT_N from the R40.2 via (B) north between the CC sense vias, west to the In2 column
T('EXP_INT_N', 0.15, B, (47.575, -11.5), (47.575, -17.25), (35.6, -17.25)); V('EXP_INT_N', 35.6, -17.25)
# port 2: R101 (OVLO top V5, R101.2 EN) kept inside the port band: V5 via, EN via -> In2 to the EN tree via; EN tree via -> Q4.3 via
T('V5', 0.3, F, 'R101.1', (-17.3, -25.0)); V('V5', -17.3, -25.0)
T('PORT2_EN', 0.15, F, 'R101.2', (-16.1, -25.0)); V('PORT2_EN', -16.1, -25.0)
T('PORT2_EN', 0.15, I2, (-16.1, -25.0), (-16.1, -29.95), (-16.8, -29.95))
T('PORT2_EN', 0.15, I2, (-16.1, -29.95), (-11.6, -29.95), (-11.6, -30.95))
# C57.1 (port-4 input bulk cap) V5 via right below the pad, inside the In2 V5 band
T('V5', 0.4, F, 'C57.1', (19.8, -25.3)); V('V5', 19.8, -25.3)
# C60 (port-5 bulk cap, below the band) V5 line up to a via in the In2 V5 band; R122.1 (port-5 OVLO divider) V5 via
T('V5', 0.25, F, 'U14.5', (29.05, -27.0), (29.13, -26.92), (29.13, -16.4), (29.35, -16.18)); V('V5', 29.13, -24.3)
T('V5', 0.25, F, (27.4, -26.2), (26.8, -26.2), (26.8, -26.6))   # to the existing port-5 V5 via
# USB_ILIM_1A5 / _3A0: F lanes west in the band, B past the MID / D5 tracks, B columns north to the R139 / R141 gate resistors
T('USB_ILIM_1A5', 0.15, F, (8.0, -17.9), (-35.5, -17.9)); V('USB_ILIM_1A5', -35.5, -17.9)
T('USB_ILIM_1A5', 0.15, B, (-35.5, -17.9), (-39.6, -17.9), (-39.6, -33.55)); V('USB_ILIM_1A5', -39.6, -33.55)
# (the via sits on the existing Q11.1 -> R139.1 track)
T('USB_ILIM_3A0', 0.15, F, (8.0, -18.5), (-36.2, -18.5)); V('USB_ILIM_3A0', -36.2, -18.5)
T('USB_ILIM_3A0', 0.15, B, (-36.2, -18.5), (-38.4, -18.5), (-38.4, -28.35)); V('USB_ILIM_3A0', -38.4, -28.35)
T('USB_ILIM_3A0', 0.15, F, (-38.4, -28.35), (-38.7, -28.65), 'R141.1')
T('PORT1_EN', 0.15, F, (-26.7, -25.94), (-26.4, -26.24))   # Q3 nudged 0.3 mm with the enlargement: extend into Q3.3
