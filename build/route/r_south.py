"""U1 south pin row (pins 27-40): pull-ups, LED, BOOT/EN switches, and the starts of the west-going long lines.
BOOT drops to B.Cu at the module edge and runs south to SW2; PWR_HOLD and SPARE37 run east on F under the module.
West-going slow lines (GAUGE, MUX_RST, CHG_INT_N, PWR_HOLD, I2C1) go to In2 lanes south of the BH2 lug, then north to In2 upper lanes y 10.85..12.9."""
from rt import T, V, PADS
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
G = 'GND'
# ---------------- BOOT: pin 27 -> R36.2 ; via (37.0,9.8) -> B col 37.3 -> y 26.5 -> via -> SW2.1
T('BOOT', 0.15, F, 'U1.27', (37.85, 9.6), 'R36.2')
T('BOOT', 0.15, F, 'R36.2', (37.3, 10.34), (37.0, 10.04), (37.0, 9.8)); V('BOOT', 37.0, 9.8)
T('BOOT', 0.15, B, (37.0, 9.8), (37.3, 10.1), (37.3, 26.5), (42.42, 26.5)); V('BOOT', 42.42, 26.5)
T('BOOT', 0.15, F, (42.42, 26.5), 'SW2.1')
# ---------------- under the module (F): PWR_HOLD y 6.8 -> via (50.2,6.3) ; SPARE37 y 7.3 -> east edge x 55.5 -> y 26.0 -> R60.1
T('PWR_HOLD', 0.15, F, 'U1.29', (40.59, 6.8), (49.7, 6.8), (50.2, 6.3)); V('PWR_HOLD', 50.2, 6.3)
T('SPARE37', 0.15, F, 'U1.30', (41.86, 7.3), (55.5, 7.3), (55.5, 26.0), (37.0, 26.0), (36.3, 25.3), 'R60.1')
T(G, 0.4, F, 'U1.40', (54.56, 10.4)); V(G, 54.56, 10.4)
# ---------------- GAUGE_ALRT_N: pin 28 -> R37.2 -> lane y 10.85 (between R36.2/R36.1) -> via (36.6,10.85) -> In2 west
T('GAUGE_ALRT_N', 0.15, F, 'U1.28', (39.2, 9.6), 'R37.2')
T('GAUGE_ALRT_N', 0.15, F, 'R37.2', (39.07, 10.85), (36.6, 10.85)); V('GAUGE_ALRT_N', 36.6, 10.85)
# 3V3: R41.1 -> lane y 9.74 (pads/R row gap) -> R37.1 -> lane y 11.2 -> R36.1 -> via
T('+3V3', 0.15, F, 'R41.1', (42.29, 9.74), (40.36, 9.74), (40.09, 10.0))
T('+3V3', 0.15, F, 'R37.1', (40.09, 11.2), (38.0, 11.2))
T('+3V3', 0.2, F, 'R36.1', (37.53, 11.36), (37.0, 11.89), (36.6, 12.0)); V('+3V3', 36.6, 12.0)
# ---------------- MUX_RST_N: pin 31 -> R41.2 -> col 43.6 -> via (43.6,16.1)
T('MUX_RST_N', 0.15, F, 'U1.31', (43.13, 9.65), (43.58, 9.95), 'R41.2')
T('MUX_RST_N', 0.15, F, 'R41.2', (43.6, 10.6), (43.6, 16.1)); V('MUX_RST_N', 43.6, 16.1)
# ---------------- LED
T('LED_STATUS', 0.15, F, 'U1.33', (45.67, 9.6), (45.87, 9.8), 'R46.1')
T('Net-(D11-A)', 0.2, F, 'R46.2', (46.19, 11.9), 'D11.2')
T(G, 0.3, F, 'D11.1', (45.2, 14.2)); V(G, 45.2, 14.2)
# ---------------- LCD lines down on F to In2 vias (J10 comb links in r_lcd)
T('LCD_RST', 0.15, F, 'U1.32', (44.4, 20.6)); V('LCD_RST', 44.4, 20.6)
T('LCD_SDCS', 0.15, F, 'U1.34', (46.94, 19.66), (46.6, 20.0)); V('LCD_SDCS', 46.6, 20.0)
T('TOUCH_INT_N', 0.15, F, 'U1.35', (48.1, 9.6), (48.01, 9.69), 'R42.2')
T('TOUCH_INT_N', 0.15, F, 'R42.2', (47.3, 10.34), (47.3, 21.2)); V('TOUCH_INT_N', 47.3, 21.2)
T('+3V3', 0.2, F, 'R42.1', (48.01, 12.1)); V('+3V3', 48.01, 12.1)
# ---------------- I2C1: pins 38/39 -> vias south
T('I2C1_SCL', 0.15, F, 'U1.38', (52.02, 12.0)); V('I2C1_SCL', 52.02, 12.0)
T('I2C1_SDA', 0.15, F, 'U1.39', (53.29, 12.6)); V('I2C1_SDA', 53.29, 12.6)
# ---------------- EN to SW3 (B col 55.3 from the under-module via)
T('EN', 0.2, B, (52.02, -6.9), (52.02, -6.62), (52.3, -6.34), (55.3, -6.34), (55.3, 27.1), (54.0, 27.1)); V('EN', 54.0, 27.1)
T('EN', 0.2, F, (54.0, 27.1), "SW3.1'")
# ---------------- In2 lanes west (south of the MID pour) and columns up to the In2 'upper lanes'
LN = [('MUX_RST_N', (43.6, 16.1), 16.1, 36.0, 11.65),
      ('CHG_INT_N', (49.48, -6.9), 17.1, 35.7, 12.45),
      ('PWR_HOLD', (50.2, 6.3), 17.5, 35.4, 13.25),
      ('I2C1_SCL', (52.02, 12.0), 17.9, 35.1, 14.05),
      ('I2C1_SDA', (53.29, 12.6), 18.3, 34.8, 14.45)]
for n, v, yl, xc, yu in LN:
    T(n, 0.15, I2, v, (v[0], yl), (xc, yl), (xc, yu))
# MUX / CHG / PWR: In2 upper lanes west to vias just west of the LCD columns, then B west
VW = {'MUX_RST_N': (26.6, 11.65), 'CHG_INT_N': (25.8, 12.45), 'PWR_HOLD': (25.0, 13.25)}
for n, (xv, y) in VW.items():
    xc = [l[3] for l in LN if l[0] == n][0]
    T(n, 0.15, I2, (xc, y), (xv, y)); V(n, xv, y)
T('I2C1_SCL', 0.15, I2, (35.1, 14.05), (8.0, 14.05))
T('I2C1_SDA', 0.15, I2, (34.8, 14.45), (9.0, 14.45))   # continues west in r_band (jog around the R63 junction via)
# GAUGE: In2 west y 10.85 -> col -11 north -> via (-11,-4.6) -> F -> R31.2
T('GAUGE_ALRT_N', 0.15, I2, (36.6, 10.85), (-11.0, 10.85), (-11.0, -4.6)); V('GAUGE_ALRT_N', -11.0, -4.6)
T('GAUGE_ALRT_N', 0.15, F, (-11.0, -4.6), (-11.96, -4.6), 'R31.2')
# B lanes west
T('MUX_RST_N', 0.15, B, (26.6, 11.65), (-6.0, 11.65))
T('CHG_INT_N', 0.15, B, (25.8, 12.45), (-19.4, 12.45)); V('CHG_INT_N', -19.4, 12.45)
T('CHG_INT_N', 0.15, I2, (-19.4, 12.45), (-19.4, -0.25)); V('CHG_INT_N', -19.4, -0.25)
T('CHG_INT_N', 0.15, B, (-19.4, -0.25), (-40.6, -0.25))
T('PWR_HOLD', 0.15, B, (25.0, 13.25), (-18.6, 13.25), (-18.6, 20.0), (-60.4, 20.0), (-60.4, 18.35))
T('PWR_BTN_N', 0.15, B, (38.05, 3.17), (27.2, 3.17), (27.2, 14.05), (-17.8, 14.05), (-17.8, 20.55), (-57.2, 20.55), (-57.2, 21.6)); V('PWR_BTN_N', -57.2, 21.6)
T('PWR_BTN_N', 0.15, F, (-57.2, 21.6), 'D14.1')
