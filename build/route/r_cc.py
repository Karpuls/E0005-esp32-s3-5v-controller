"""CC1 / CC2 sense dividers (R131/R132 north of U1) to the USB-C side (R129/R130 at J11).
CC1: F west y -20.6, CC2: B west y -20.4 (crossing hop), F south to vias north of the USB pair, In2 diagonals under the pair,
B west at y -1.9 / -1.1, B south at x -18.4 / -18.0, B west at y 7.3 / 7.7, north to y 3.9 / 5.4 and into the J11 corner."""
from rt import T, V
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
V('CC1', 49.6, -17.89)
# short In2 hop inside the (here unloaded) east end of the In2 V5 band, past the R131/R132 column and the CC2 via
T('CC1', 0.15, I2, (49.6, -17.89), (44.5, -17.89)); V('CC1', 44.5, -17.89)
T('CC1', 0.15, F, (44.5, -17.89), (44.5, -19.2), (33.9, -19.2), (33.9, -10.1)); V('CC1', 33.9, -10.1)
T('CC2', 0.15, B, (47.55, -20.4), (33.3, -20.4)); V('CC2', 33.3, -20.4)
T('CC2', 0.15, F, (33.3, -20.4), (33.3, -11.6)); V('CC2', 33.3, -11.6)
# In2 west on the north side of the BH1 peg, south under the USB pair at x 28.4 / 27.6
T('CC1', 0.15, I2, (33.9, -10.1), (28.4, -10.1), (28.4, -1.9)); V('CC1', 28.4, -1.9)
T('CC2', 0.15, I2, (33.3, -11.6), (27.6, -11.6), (27.6, -1.1)); V('CC2', 27.6, -1.1)
T('CC1', 0.15, B, (28.4, -1.9), (-18.4, -1.9), (-18.4, 7.3), (-38.2, 7.3), (-38.2, 5.1), (-52.3, 5.1), (-52.3, 2.6)); V('CC1', -52.3, 2.6)
T('CC2', 0.15, B, (27.6, -1.1), (-18.0, -1.1), (-18.0, 7.7), (-38.6, 7.7), (-38.6, 5.8), (-52.4, 5.8), (-52.4, 7.7)); V('CC2', -52.4, 7.7)
T('CC2', 0.15, B, (-52.4, 6.0), (-54.0, 6.0)); V('CC2', -54.0, 6.0)
T('CC1', 0.15, F, (-52.3, 2.6), (-52.3, 2.91), 'R129.1', 'J11.A5')
T('CC2', 0.15, F, (-52.4, 7.7), (-52.8, 7.7), 'R130.1')
T('CC2', 0.15, F, (-54.0, 6.0), (-54.25, 6.25), 'J11.B5')
