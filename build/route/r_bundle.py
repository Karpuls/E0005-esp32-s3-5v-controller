"""U2 bundle east (CHG_TS / I2C0_SCL / I2C0_SDA / CHG_CD, F.Cu) and the I2C0 / CHG_CD links north to U9 on In2 (new frame).
F lanes leave the U2 stubs at x -40.6, re-order north of the BH2 peg (TS -0.85, SCL 0.35, SDA 0.95, CD 1.6) and run east to the
centre: TS into RT1.1, SCL up to R30.2, SDA / CD to vias that join In2 lanes (y 2.4 / 1.6) from U9; SCL's In2 lane (y 2.0) joins at x -8.5."""
import rt
rt.NEWFRAME = True
from rt import T, V
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
# ---- F lanes from the U2 stubs
T('CHG_TS', 0.15, F, (-40.6, 1.5), (-35.9, 1.5), (-33.55, -0.85), (-7.3, -0.85), (-6.45, 0.0), 'RT1.1')
T('I2C0_SCL', 0.15, F, (-40.6, 2.2), (-35.5, 2.2), (-33.65, 0.35), (-8.5, 0.35)); V('I2C0_SCL', -8.5, 0.35)
T('I2C0_SDA', 0.15, F, (-40.6, 2.5), (-35.0, 2.5), (-33.45, 0.95), (-9.3, 0.95)); V('I2C0_SDA', -9.3, 0.95)
T('CHG_CD', 0.15, F, (-40.6, 2.8), (-34.5, 2.8), (-33.3, 1.6), (-7.6, 1.6)); V('CHG_CD', -7.6, 1.6)
# ---- In2 north to U9 (3V3 plane, short of the V5 band)
T('I2C0_SCL', 0.15, I2, (13.65, -15.78), (13.65, 2.25), (-8.5, 2.25), (-8.5, -3.0), (-9.26, -3.76), (-9.26, -4.6)); V('I2C0_SCL', -9.26, -4.6)
T('I2C0_SCL', 0.15, F, (-9.26, -4.6), 'R30.2')   # R30.2 from the south (F lanes stay clear of CHG_TS)
T('I2C0_SDA', 0.15, I2, (14.45, -16.42), (15.0, -15.87), (15.0, 2.65), (-9.3, 2.65), (-9.3, 0.95))
T('CHG_CD', 0.15, I2, (7.95, -11.875), (6.2, -11.875), (6.2, 1.6), (-7.6, 1.6))
# ---- SDA up to R29.2: In2 north under the R29/R30 column to a via north of R32, F back down through the R32 pad gap
T('I2C0_SDA', 0.15, I2, (-9.3, 0.95), (-9.85, 0.4), (-9.85, -10.81), (-9.46, -11.2)); V('I2C0_SDA', -9.46, -11.2)
T('I2C0_SDA', 0.15, F, (-9.46, -11.2), (-9.46, -9.4))   # down the 0.48 mm gap between R32.1 and R32.2 into R29.2
# I2C0 to U1: SDA F diagonal from the L0 lane end into the B channel between the two MID lines, B SW/west to the SDA In2 column;
# SCL In2 from the R45.2 via south of the CC1/CC2 In2 columns, west to a B hop over the SDA column onto the SCL column
T('I2C0_SDA', 0.15, F, (37.0, -9.785), (34.6, -12.185), (34.6, -12.9)); V('I2C0_SDA', 34.6, -12.9)
T('I2C0_SDA', 0.15, B, (34.6, -12.9), (33.575, -12.9), (24.475, -3.8), (15.0, -3.8)); V('I2C0_SDA', 15.0, -3.8)
T('I2C0_SCL', 0.15, I2, (33.6, -4.65), (32.8, -4.65), (32.8, -0.3), (16.0, -0.3)); V('I2C0_SCL', 16.0, -0.3)
T('I2C0_SCL', 0.15, B, (16.0, -0.3), (13.65, -0.3)); V('I2C0_SCL', 13.65, -0.3)
