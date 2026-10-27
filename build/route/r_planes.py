"""Inner-layer planes: In1 solid GND (no tracks); In2 split into V5 (west column + north port band) and 3V3 (middle/east).
Special In2 strips/pours (VBUS, BAT+, pack path, MID, CELL2_P) are higher-priority zones in their modules."""
from rt import T, V, VS, Z, rect
I1, I2 = 'In1.Cu', 'In2.Cu'
Z('GND', I1, rect(-62.5, -32.5, 62.5, 32.5), 'R_GND_IN1', prio=0, conn='pth', clr=0.25)
Z('V5', I2, [(-62.5, -32.5), (62.5, -32.5), (62.5, -17.0), (-28.3, -17.0), (-28.3, -16.0), (-29.7, -16.0), (-29.7, -17.0), (-38.5, -17.0), (-38.5, 32.5), (-62.5, 32.5)],
  'R_V5_IN2', prio=1, conn='full', clr=0.25)
Z('+3V3', I2, [(-38.5, -17.0), (-29.7, -17.0), (-29.7, -16.0), (-28.3, -16.0), (-28.3, -17.0), (62.5, -17.0), (62.5, 32.5), (-38.5, 32.5)], 'R_3V3_IN2', prio=1, conn='full', clr=0.25)
