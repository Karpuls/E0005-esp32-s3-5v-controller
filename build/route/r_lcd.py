"""U1 west pin column (pins 17-25), LCD connector J10 and its pull-ups.
J10 fine-pitch pins get a via comb under the connector body: even pins row A (y 26.85), odd pins row B (y 27.75),
0.5/0.3 vias, so a stub from a row-A via passes between two row-B vias with 0.175 mm clearance.
LCD lines leave U1 on F.Cu, spread to 0.9 mm pitch south of the cells' peg, then drop to B.Cu / In2 and reach the comb."""
from rt import T, V, Z, PADS
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
G = 'GND'
VA, VB = 26.85, 27.75
def jx(n):
    return 25.75 + 0.5 * (n - 1)
def comb(net, pin):
    y = VA if pin % 2 == 0 else VB
    T(net, 0.15, F, 'J10.%d' % pin, (jx(pin), y)); V(net, jx(pin), y, dia=0.5, drill=0.3)
    return (jx(pin), y)
# ---------------- west column local
T('I2C0_SCL', 0.15, F, 'U1.17', (35.6, -4.45), (35.4, -4.65), 'R45.2')
T('I2C0_SCL', 0.15, F, 'R45.2', (33.6, -4.65)); V('I2C0_SCL', 33.6, -4.65)
T('+3V3', 0.2, F, 'R45.1', (33.6, -3.63)); V('+3V3', 33.6, -3.63)
T('LCD_MOSI_MCU', 0.15, F, 'U1.19', (35.79, -1.91), (35.79, -2.45), (34.2, -2.45)); V('LCD_MOSI_MCU', 34.2, -2.45)
T('LCD_MOSI_MCU', 0.15, B, (34.2, -2.45), (34.2, -5.67)); V('LCD_MOSI_MCU', 34.2, -5.67)
T('LCD_MOSI_MCU', 0.15, F, (34.2, -5.67), 'R56.1')
T('LCD_SCK_MCU', 0.15, F, 'U1.20', (35.6, -0.64), (35.5, -0.74), 'R55.1')
T('PWR_BTN_N', 0.15, F, 'U1.23', (35.6, 3.17), (35.4, 2.97), 'R43.2')
T('+3V3', 0.2, F, 'R43.1', (34.3, 3.99)); V('+3V3', 34.3, 3.99)
# PWR_BTN_N leaves through a via under the module edge (B west)
T('PWR_BTN_N', 0.15, F, 'U1.23', (38.05, 3.17)); V('PWR_BTN_N', 38.05, 3.17)
# ---------------- LCD lines: exits -> spread to final columns (F)
XF = {'LCD_MOSI': 27.6, 'LCD_CS': 28.5, 'LCD_SCK': 29.4, 'LCD_MISO': 31.5, 'LCD_DC': 32.4, 'LCD_LITE': 33.3}
T('LCD_MOSI', 0.15, F, 'R56.2', (32.7, -6.69), (32.7, -2.1), (XF['LCD_MOSI'], 3.0))
T('LCD_CS', 0.15, F, 'U1.18', (35.79, -3.1), (33.05, -3.1), (33.05, -1.9), (XF['LCD_CS'], 2.65))
T('LCD_SCK', 0.15, F, 'R55.2', (33.4, -1.76), (XF['LCD_SCK'], 2.24))
T('LCD_MISO', 0.15, F, 'U1.21', (35.6, 0.63), (XF['LCD_MISO'], 0.63))
T('LCD_DC', 0.15, F, 'U1.22', (35.6, 1.91), (XF['LCD_DC'], 1.91))
T('LCD_LITE', 0.15, F, 'U1.24', (35.6, 4.6), (XF['LCD_LITE'], 4.6))
# EXP_INT_N from pin 25: via just west of the pad, B north under the USB pair (joins the R40.2 branch, r_east)
T('EXP_INT_N', 0.15, F, 'U1.25', (35.6, 5.71)); V('EXP_INT_N', 35.6, 5.71)
# drop vias (B.Cu continues to the J10 comb)
VY = {'LCD_DC': 15.2, 'LCD_MISO': 15.8, 'LCD_MOSI': 16.4, 'LCD_SCK': 17.0, 'LCD_LITE': 17.6, 'LCD_CS': 19.6}
for n, x in XF.items():
    y0 = {'LCD_MOSI': 3.0, 'LCD_CS': 2.65, 'LCD_SCK': 2.24, 'LCD_MISO': 0.63, 'LCD_DC': 1.91, 'LCD_LITE': 4.6}[n]
    T(n, 0.15, F, (x, y0), (x, VY[n])); V(n, x, VY[n])
# ---------------- J10 top-fed pins and pull-ups
T('+3V3', 0.3, F, 'C42.1', (25.75, 24.4), 'J10.1')
T('+3V3', 0.3, F, 'C42.1', (24.2, 23.68)); V('+3V3', 24.2, 23.68)
T(G, 0.3, F, 'C42.2', (24.2, 21.78)); V(G, 24.2, 21.78)
T('+3V3', 0.2, F, 'R59.1', (27.83, 22.0)); V('+3V3', 27.83, 22.0)
T('LCD_SDCS', 0.15, F, 'R59.2', (27.83, 24.6), (30.25, 24.6), 'J10.10')
T('LCD_MEMCS', 0.15, F, 'R57.2', (32.7, 23.88), (32.7, 24.6), (30.75, 24.6), 'J10.11')
T('EYESPI_GP1', 0.15, F, 'R60.2', (35.28, 24.8), (33.75, 24.8), 'J10.17')
T('+3V3', 0.25, F, 'R57.1', (34.35, 23.88), (34.35, 22.63), 'R58.1')
T('+3V3', 0.25, F, 'R58.1', (34.41, 21.7)); V('+3V3', 34.41, 21.7)
T('LCD_TSCS', 0.15, F, 'R58.2', (33.39, 21.65)); V('LCD_TSCS', 33.39, 21.65)
T(G, 0.3, F, 'J10.3', (26.75, VB)); V(G, 26.75, VB, dia=0.5, drill=0.3)
for n, p in (('LCD_LITE', 2), ('LCD_SCK', 4), ('LCD_MOSI', 5), ('LCD_MISO', 6), ('LCD_DC', 7), ('LCD_RST', 8), ('LCD_CS', 9),
             ('LCD_SDCS', 10), ('LCD_TSCS', 12), ('LCD_SCL', 13), ('LCD_SDA', 14), ('TOUCH_INT_N', 15)):
    comb(n, p)
# ---------------- B west-U (pins 2,4,5,6,7): comb -> lanes south of the comb -> west columns -> north -> east to drop vias
WU = [('LCD_LITE', 2, 28.3, 23.2), ('LCD_SCK', 4, 28.6, 22.9), ('LCD_MOSI', 5, 28.9, 22.6), ('LCD_MISO', 6, 29.2, 22.3), ('LCD_DC', 7, 29.5, 22.0)]
for n, p, yl, xc in WU:
    yv = VA if p % 2 == 0 else VB
    T(n, 0.15, B, (jx(p), yv), (jx(p), yl), (xc, yl), (xc, VY[n]), (XF[n], VY[n]))
# ---------------- B east-U (pins 9 CS, 12 TSCS)
T('LCD_TSCS', 0.15, B, (jx(12), VA), (jx(12), 28.3), (35.6, 28.3), (35.6, 21.0), (33.39, 21.0), (33.39, 21.65))
T('LCD_CS', 0.15, B, (jx(9), VB), (jx(9), 28.6), (35.9, 28.6), (35.9, 19.95), (XF['LCD_CS'], 19.95), (XF['LCD_CS'], VY['LCD_CS']))
# ---------------- In2: RST / SDCS / TOUCH from the U1 south-row vias, lanes between the BH2 peg and the comb
for n, v, yl, p in (('LCD_RST', (44.4, 20.6), 24.4, 8), ('LCD_SDCS', (46.6, 20.0), 24.9, 10), ('TOUCH_INT_N', (47.3, 21.2), 25.4, 15)):
    T(n, 0.15, I2, v, (v[0], yl), (jx(p), yl), (jx(p), VA if p % 2 == 0 else VB))
# In2 west-U for LCD_SCL / LCD_SDA (columns x 21.4 / 21.1 continue north towards U8)
for n, p, yl, xc in (('LCD_SCL', 13, 28.3, 21.4), ('LCD_SDA', 14, 28.6, 21.1)):
    T(n, 0.15, I2, (jx(p), VA if p % 2 == 0 else VB), (jx(p), yl), (xc, yl), (xc, 20.0))
