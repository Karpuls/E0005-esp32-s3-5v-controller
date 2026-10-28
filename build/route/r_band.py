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
T('PORT2_OFF', 0.15, F, (8.2, -20.1), (-8.8, -20.1)); V('PORT2_OFF', -8.8, -20.1)   # B column north frees F for the FLT lanes
T('PORT2_OFF', 0.15, B, (-8.8, -20.1), (-8.8, -26.9)); V('PORT2_OFF', -8.8, -26.9)
T('PORT2_OFF', 0.15, F, (-8.8, -26.9), 'R82.2')
# PORT4_OFF: F lane y -20.9 -> via -> B col x 4.0 -> via -> F into Q6.1 (west side)
T('PORT4_OFF', 0.15, F, (8.6, -20.9), (4.3, -20.9)); V('PORT4_OFF', 4.3, -20.9)
T('PORT4_OFF', 0.15, B, (4.3, -20.9), (4.0, -21.2), (4.0, -30.15), (4.4, -30.55)); V('PORT4_OFF', 4.4, -30.55)
T('PORT4_OFF', 0.15, F, (4.4, -30.55), (5.4, -30.55))
# PORT3_OFF: Q5.1 -> via -> B across the band -> via -> F to R84.2 (keeps F free for the west lanes)
T('PORT3_OFF', 0.15, F, 'Q5.1', (5.17, -24.62), (6.0, -24.62)); V('PORT3_OFF', 6.0, -24.62)
T('PORT3_OFF', 0.15, B, (6.0, -24.62), (5.6, -24.22), (5.6, -16.9)); V('PORT3_OFF', 5.6, -16.9)
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
T(G, 0.3, F, 'Q7.2', (25.3, -25.19)); V(G, 25.3, -25.19)   # Q7.2 GND via next to the pad (was stretched 8 mm by the enlargement)
# PORT1-4_FLT_N: U9.13-.16 F east under/past the pull-up row to nested F columns x 20.7..23.35, north into the band,
# F lanes y -21.5 (P4) .. -23.3 (P1) west; P3 / P2 / P1 drop to B for the last leg (port EN/V5 parts on F)
for pin, n, xc, yl in (('U9.16', 'PORT4_FLT_N', 20.7, -21.5), ('U9.15', 'PORT3_FLT_N', 21.3, -22.05),
                       ('U9.14', 'PORT2_FLT_N', 22.75, -22.6), ('U9.13', 'PORT1_FLT_N', 23.35, -23.15)):
    T(n, 0.15, F, pin, (xc, rt.PADS_NEW[pin]['y']), (xc, yl))
T('PORT4_FLT_N', 0.15, F, (20.7, -21.5), (12.0, -21.5)); V('PORT4_FLT_N', 12.0, -21.5)   # B under the P3..P1 lanes
T('PORT4_FLT_N', 0.15, B, (12.0, -21.5), (12.0, -26.1), (12.3, -26.4)); V('PORT4_FLT_N', 12.3, -26.4)
T('PORT4_FLT_N', 0.15, F, (12.3, -26.4), (12.3, -27.01))
T('PORT3_FLT_N', 0.15, F, (21.3, -22.05), (-5.6, -22.05)); V('PORT3_FLT_N', -5.6, -22.05)
T('PORT3_FLT_N', 0.15, B, (-5.6, -22.05), (-5.6, -26.0), (-5.0, -26.6)); V('PORT3_FLT_N', -5.0, -26.6)
T('PORT3_FLT_N', 0.15, F, (-5.0, -26.6), (-5.0, -27.01))
T('PORT2_FLT_N', 0.15, F, (22.75, -22.6), (-18.18, -22.6)); V('PORT2_FLT_N', -18.18, -22.6)
T('PORT2_FLT_N', 0.15, B, (-18.18, -22.6), (-18.18, -25.55))
T('PORT1_FLT_N', 0.15, F, (23.35, -23.15), (-20.7, -23.15)); V('PORT1_FLT_N', -20.7, -23.15)
T('PORT1_FLT_N', 0.15, B, (-20.7, -23.15), (-20.7, -24.1), (-21.2, -24.6), (-32.5, -24.6), (-34.4, -26.5))
# PORT5_FLT_N: under-body via -> B east under the pull-up row, south of the 3V3 via at (30.6,-16.6), north to the R89.2 via
T('PORT5_FLT_N', 0.15, B, (14.45, -12.525), (14.85, -12.125), (29.9, -12.125), (31.3, -13.525), (31.3, -25.7), (30.6, -26.4))
# USBIN_FLT_N: R90.2 -> F between the pull-up pads -> via -> B east of the 3V3 riser -> northmost F lane y -23.7 west ->
# In2 north of the BH1 peg (south of the PORT1_EN via) and along y -24.0 into the V5 west column to the U16.4 via
T('USBIN_FLT_N', 0.15, F, 'R90.2', (17.43, -13.5), (20.0, -13.5)); V('USBIN_FLT_N', 20.0, -13.5)
T('USBIN_FLT_N', 0.15, B, (20.0, -13.5), (22.6, -13.5), (22.6, -23.7)); V('USBIN_FLT_N', 22.6, -23.7)
T('USBIN_FLT_N', 0.15, F, (22.6, -23.7), (-21.5, -23.7)); V('USBIN_FLT_N', -21.5, -23.7)
T('USBIN_FLT_N', 0.15, I2, (-21.5, -23.7), (-22.95, -25.15), (-26.6, -25.15), (-27.15, -24.6), (-32.8, -24.6), (-33.4, -24.0),
  (-50.23, -24.0), (-50.23, -29.2))
# CHG_PG_N: R92.2 -> F north of R92 -> via -> B north -> F band lane y -19.8 / -21.5 west -> B hop past the P1_OFF column ->
# F y -19.9 south of the BH1 peg -> In2 west of the ILIM vias -> B column x -38.0 west of the BH1.2 holder pad ->
# In2 hop under the MID B line -> B to the existing stub at (-40.6, 0.45)
T('CHG_PG_N', 0.15, F, 'R92.2', (17.43, -14.71), (19.9, -14.71)); V('CHG_PG_N', 19.9, -14.71)
T('CHG_PG_N', 0.15, B, (19.9, -14.71), (19.9, -19.8)); V('CHG_PG_N', 19.9, -19.8)
T('CHG_PG_N', 0.15, F, (19.9, -19.8), (11.2, -19.8), (9.5, -21.5), (-21.6, -21.5)); V('CHG_PG_N', -21.6, -21.5)
T('CHG_PG_N', 0.15, B, (-21.6, -21.5), (-23.2, -19.9)); V('CHG_PG_N', -23.2, -19.9)
T('CHG_PG_N', 0.15, F, (-23.2, -19.9), (-35.9, -19.9)); V('CHG_PG_N', -35.9, -19.9)
T('CHG_PG_N', 0.15, I2, (-35.9, -19.9), (-38.0, -17.8), (-38.0, -10.4)); V('CHG_PG_N', -38.0, -10.4)
T('CHG_PG_N', 0.15, B, (-38.0, -10.4), (-38.0, -3.0)); V('CHG_PG_N', -38.0, -3.0)
T('CHG_PG_N', 0.15, I2, (-38.0, -3.0), (-38.0, 0.9)); V('CHG_PG_N', -38.0, 0.9)
T('CHG_PG_N', 0.15, B, (-38.0, 0.9), (-40.15, 0.9), (-40.6, 0.45))
# BUCK_PG: R93.2 -> via in the pull-up pocket -> In2 south (3V3 plane) -> B west along y -5.85 (north of the MID B line,
# south of the U8 via field) -> In2 down x -20.0 (east of the CELL2_P In2 line) and west along y 16.0 (south of BH2 / BAT+ strip)
# to the U17.4 via
T('BUCK_PG', 0.15, F, 'R93.2', (18.8, -15.25), (19.1, -15.55)); V('BUCK_PG', 19.1, -15.55)
T('BUCK_PG', 0.15, I2, (19.1, -15.55), (18.6, -15.05), (18.6, -6.2)); V('BUCK_PG', 18.6, -6.2)
T('BUCK_PG', 0.15, B, (18.6, -6.2), (18.25, -5.85), (-19.75, -5.85), (-20.0, -6.1)); V('BUCK_PG', -20.0, -6.1)
T('BUCK_PG', 0.15, I2, (-20.0, -6.1), (-20.0, 16.0), (-51.0, 16.0), (-51.55, 15.45))
# PORT5_SCL / _SDA: U8 east via column -> B south under the pull-up row -> B lanes y -7.0 / -7.6 east (between the 3V3 vias and
# the BUCK_PG lane) -> F columns x 24.4 / 23.8 north (east of the FLT columns) -> B past Q7 -> R127.1 / R128.1 (port-5 pull-ups)
T('PORT5_SDA', 0.15, B, (-1.55, -9.925), (-1.55, -7.6), (23.8, -7.6)); V('PORT5_SDA', 23.8, -7.6)
T('PORT5_SDA', 0.15, F, (23.8, -7.6), (23.8, -23.75)); V('PORT5_SDA', 23.8, -23.75)
T('PORT5_SDA', 0.15, B, (23.8, -23.75), (23.2, -24.35), (23.2, -31.6)); V('PORT5_SDA', 23.2, -31.6)
T('PORT5_SDA', 0.15, F, (23.2, -31.6), (22.61, -32.19), 'R128.1')
T('PORT5_SCL', 0.15, B, (-2.45, -10.575), (-2.45, -7.0), (24.4, -7.0)); V('PORT5_SCL', 24.4, -7.0)
T('PORT5_SCL', 0.15, F, (24.4, -7.0), (24.4, -24.35)); V('PORT5_SCL', 24.4, -24.35)
T('PORT5_SCL', 0.15, B, (24.4, -24.35), (23.8, -24.95), (23.8, -30.1)); V('PORT5_SCL', 23.8, -30.1)
T('PORT5_SCL', 0.15, F, (23.8, -30.1), 'R127.1')
# PORT3_SDA: from the U8 col-A via lane west to a B column x -7.95 between the PORT2_OFF vias and the PORT1_SCL column, north to
# R114.1 (R64.1 3V3 via moved off the column)
T('+3V3', 0.25, F, 'R64.1', (-7.95, -16.55), (-8.6, -17.2)); V('+3V3', -8.6, -17.2)
T('PORT3_SDA', 0.15, B, (-6.45, -12.53), (-7.95, -12.53), (-7.95, -32.44)); V('PORT3_SDA', -7.95, -32.44)
T('PORT3_SDA', 0.15, F, (-7.95, -32.44), 'R114.1')
# PORT3_SCL: U8 col-B via -> B channel x -3.0 between the via columns -> band column x -0.2 -> lane y -31.05 west -> R113.1
T('PORT3_SCL', 0.15, B, (-3.55, -11.875), (-3.0, -12.425), (-3.0, -17.6), (-0.2, -20.4), (-0.2, -31.05), (-6.05, -31.05))
V('PORT3_SCL', -6.05, -31.05); T('PORT3_SCL', 0.15, F, (-6.05, -31.05), 'R113.1')
# PORT4_SDA / _SCL: taps on the pull-up links south of U8 (In2) -> vias west of R73 -> B columns past U8's east side ->
# band columns x 1.0 / 1.6 -> lanes north of the 3V3 riser via -> R121.1 / R120.1
T('PORT4_SDA', 0.15, I2, (-4.75, -6.6), (-4.15, -7.2), (0.0, -7.2), (0.55, -7.75), (0.55, -8.2)); V('PORT4_SDA', 0.55, -8.2)
T('PORT4_SDA', 0.15, B, (0.55, -8.2), (-0.05, -8.8), (-0.05, -17.4), (1.0, -18.45), (1.0, -33.0), (3.2, -33.0), (3.2, -34.0), (6.55, -34.0))
V('PORT4_SDA', 6.55, -34.0); T('PORT4_SDA', 0.15, F, (6.55, -34.0), 'R121.1')
T('PORT4_SCL', 0.15, I2, (-3.55, -9.2), (0.55, -9.2)); V('PORT4_SCL', 0.55, -9.2)
T('PORT4_SCL', 0.15, B, (0.55, -9.2), (0.55, -17.4), (1.6, -18.45), (1.6, -32.5), (11.2, -32.5), (11.3, -32.6)); V('PORT4_SCL', 11.3, -32.6)
T('PORT4_SCL', 0.15, F, (11.3, -32.6), (11.1, -32.4), (11.1, -31.06), 'R120.1')
# LCD_SCL / LCD_SDA (U8 -> J10): In2 columns x 3.6 / 2.06 south of U8 (between the pull-up 3V3 vias and the CHG_CD column) ->
# B under the USB pair -> F diagonals over the I2C1 / MUX / CHG / PWR lanes -> the J10 In2 columns x 21.4 / 21.1
T('LCD_SDA', 0.15, I2, (-1.55, -11.225), (1.6, -11.225), (2.06, -10.765), (2.06, 0.9)); V('LCD_SDA', 2.06, 0.9)
T('LCD_SDA', 0.15, F, 'R74.2', (-1.75, -8.46), (-1.75, -6.45)); V('LCD_SDA', -1.75, -6.45)   # pull-up R74
T('LCD_SDA', 0.15, I2, (-1.75, -6.45), (2.06, -6.45))
T('LCD_SDA', 0.15, B, (2.06, 0.9), (2.06, 10.2)); V('LCD_SDA', 2.06, 10.2)
T('LCD_SDA', 0.15, F, (2.06, 10.2), (2.06, 10.8), (12.4, 10.8), (20.5, 18.9), (20.5, 19.4)); V('LCD_SDA', 20.5, 19.4)
T('LCD_SDA', 0.15, I2, (20.5, 19.4), (21.1, 20.0))
T('LCD_SCL', 0.15, F, 'R75.2', (3.2, -10.08), (3.2, -8.9), (3.6, -8.5)); V('LCD_SCL', 3.6, -8.5)
T('LCD_SCL', 0.15, I2, (3.6, -8.5), (3.6, 0.9)); V('LCD_SCL', 3.6, 0.9)
T('LCD_SCL', 0.15, B, (3.6, 0.9), (3.6, 10.2)); V('LCD_SCL', 3.6, 10.2)
T('LCD_SCL', 0.15, F, (3.6, 10.2), (13.0, 10.2), (21.4, 18.6)); V('LCD_SCL', 21.4, 18.6)
T('LCD_SCL', 0.15, I2, (21.4, 18.6), (21.4, 20.0))
# MUX_RST_N: U8.3 via -> In2 west along y -16.0 (north of the U8 west vias) -> In2 column x -11.55 (west of the GAUGE column)
# south to the B lane from U1 (y 11.65)
T('MUX_RST_N', 0.15, I2, (-3.55, -15.775), (-3.775, -16.0), (-11.55, -16.0), (-11.55, 10.0)); V('MUX_RST_N', -11.55, 10.0)
T('MUX_RST_N', 0.15, B, (-11.55, 10.0), (-9.9, 11.65), (-6.0, 11.65))
# SW1_IN / SW2_IN (U1 pull-up side -> J6 / J7 button connectors): B columns under the east half of U1 (east of the MID B pour),
# south past the U1 south vias, west along the south edge (y 30.9 / 31.75) -> via -> F up to the connector pin; F links to the ESD
# diode and the pull-up at the connector
T('SW1_IN', 0.15, B, (43.35, -13.35), (45.5, -13.35), (45.5, 10.8), (49.0, 14.3), (49.0, 29.4), (47.5, 30.9), (-26.63, 30.9))
V('SW1_IN', -26.63, 30.9); T('SW1_IN', 0.15, F, (-26.63, 30.9), 'J6.1')
T('SW1_IN', 0.15, F, 'J6.1', (-26.63, 25.65), 'D15.1'); T('SW1_IN', 0.15, F, 'R47.2', (-26.6, 25.41))
T('SW2_IN', 0.15, B, (44.1, -14.1), (46.0, -14.1), (46.0, 9.0), (49.6, 12.6), (49.6, 29.8), (47.65, 31.75), (-16.63, 31.75))
V('SW2_IN', -16.63, 31.75); T('SW2_IN', 0.15, F, (-16.63, 31.75), 'J7.1')
T('SW2_IN', 0.15, F, 'J7.1', (-16.63, 25.65), 'D16.1'); T('SW2_IN', 0.15, F, 'R49.2', (-16.6, 25.41))
# SW3_IN / SW4_IN: vias north of R52 / R54 -> In2 columns between the EXP_INT_N column and the MID In2 pour, down the west side of
# U1 -> In2 west south of the USB pair -> vias west of the LCD F lines -> F south to the J8 / J9 ESD diode, pull-up and connector pin
T('SW3_IN', 0.15, F, 'R52.1', (36.6, -14.5)); V('SW3_IN', 36.6, -14.5)
T('SW3_IN', 0.15, I2, (36.6, -14.5), (36.6, 7.0), (36.0, 7.6), (0.8, 7.6)); V('SW3_IN', 0.8, 7.6)
T('SW3_IN', 0.15, F, (0.8, 7.6), (0.8, 23.5), (-5.6, 23.5), (-5.6, 25.37), 'D17.1')
T('SW3_IN', 0.15, F, 'D17.1', (-6.35, 25.9), (-6.63, 26.18), 'J8.1'); T('SW3_IN', 0.15, F, 'R51.2', (-6.4, 25.41))
T('SW4_IN', 0.15, F, 'R54.1', (37.66, -15.5)); V('SW4_IN', 37.66, -15.5)
T('SW4_IN', 0.15, I2, (37.66, -15.5), (37.66, -14.0), (37.95, -13.71), (37.95, 2.3), (37.3, 2.95), (37.3, 7.6), (36.7, 8.2), (1.4, 8.2))
V('SW4_IN', 1.4, 8.2); T('SW4_IN', 0.15, F, (1.4, 8.2), (1.4, 24.0), (2.31, 24.91), 'R53.2')
T('SW4_IN', 0.15, F, 'R53.2', (3.6, 25.41)); T('SW4_IN', 0.15, F, 'D18.1', (3.65, 25.9), (3.37, 26.18), 'J9.1')
# BAT+ sense for the gauge VBATT filter (R28.1): In2 out of the BAT+ strip -> B east (south of the MID B line) -> In2 hop under the
# CHG_G column -> B along y -9.2 (between the B_N via and the CHG_G lane) -> F into R28.1
T('BAT+', 0.2, I2, (-40.2, -8.2), (-36.3, -8.2)); V('BAT+', -36.3, -8.2)
T('BAT+', 0.2, B, (-36.3, -8.2), (-29.4, -8.2)); V('BAT+', -29.4, -8.2)
T('BAT+', 0.2, I2, (-29.4, -8.2), (-29.0, -8.6), (-27.6, -8.6)); V('BAT+', -27.6, -8.6)
T('BAT+', 0.2, B, (-27.6, -8.6), (-27.0, -9.2), (-18.6, -9.2)); V('BAT+', -18.6, -9.2)
T('BAT+', 0.2, F, (-18.6, -9.2), (-17.82, -8.42), 'R28.1')
