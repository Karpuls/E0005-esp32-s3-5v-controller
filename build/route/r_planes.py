"""Inner-layer planes: In1 solid GND (no tracks); In2 split into V5 (west column + north port band) and 3V3 (middle/east).
Special In2 strips/pours (VBUS, BAT+, pack path, MID, CELL2_P) are higher-priority zones in their modules."""
from rt import T, V, VS, Z, rect
import rt as _rt
_rt.NEWFRAME = True   # planes redrawn in the enlarged 125 x 73 frame (north edge at y -40.5)
I1, I2 = 'In1.Cu', 'In2.Cu'
Z('GND', I1, rect(-62.5, -40.5, 62.5, 32.5), 'R_GND_IN1', prio=0, conn='pth', clr=0.25)
Z('V5', I2, [(-62.5, -40.5), (-38.5, -40.5), (-38.5, -31.0), (52.5, -31.0), (52.5, -17.0), (-28.3, -17.0), (-28.3, -16.0),
            (-29.7, -16.0), (-29.7, -17.0), (-38.5, -17.0), (-38.5, 32.5), (-62.5, 32.5)], 'R_V5_IN2', prio=1, conn='full', clr=0.25)
Z('V5', I2, rect(-1.5, -33.2, -0.3, -31.0), 'R_V5B_C54', prio=1, conn='full', clr=0.25)
Z('+3V3', I2, [(-38.5, -17.0), (-29.7, -17.0), (-29.7, -16.0), (-28.3, -16.0), (-28.3, -17.0), (62.5, -17.0), (62.5, 32.5), (-38.5, 32.5)], 'R_3V3_IN2', prio=1, conn='full', clr=0.25)
