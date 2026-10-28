"""Cleanup fixes (final frame): In2 3V3 plane bridges where signal lanes on In2 split the plane, missing 3V3 feeds."""
import rt
rt.NEWFRAME = True
from rt import T, V
F, B, I2 = 'F.Cu', 'B.Cu', 'In2.Cu'
P = '+3V3'
def bridge(a, b, *mid, layer=F, w=0.25):
    """two 3V3 vias in different In2 plane pieces, linked on an outer layer"""
    V(P, *a); V(P, *b); T(P, w, layer, a, *mid, b)
bridge((-29.0, 10.4), (-26.0, 16.8), (-26.0, 13.4))      # west piece (charger / buck side) <-> south main, over CELL2_P + BUCK_PG In2
bridge((-17.0, -15.2), (-15.8, -15.2))                    # band-edge strip <-> strip inside the I2C1 loop (over I2C1_SDA In2)
bridge((-12.6, 11.6), (-12.6, 15.2))                      # inside the I2C1 / GAUGE loops <-> south main (over I2C1 lanes)
bridge((1.2, -3.0), (4.9, -3.0))                          # U8 pull-up area <-> centre (over the LCD In2 columns)
T(P, 0.25, F, 'R73.1', 'R75.1')                           # R73.1's via sits in a small piece: share R75.1's
T(P, 0.2, F, 'C44.1@0,0.2', (1.95, -15.41), (2.07, -15.29), (2.07, -14.75), (2.21, -14.61), 'R62.1')   # U8 decoupling / U8.24 to R62.1 (its via is in the main plane)
T(P, 0.2, B, (8.36, -26.0), (7.6, -26.0))                 # R87.1 (band pull-up) onto the x 7.6 3V3 riser
for p, v in (('R47.1', (-28.71, 24.4)), ('R49.1', (-18.71, 24.4)), ('R51.1', (-8.71, 24.4)), ('R53.1', (1.29, 26.3))):
    T(P, 0.25, F, p, v); V(P, *v)                          # button pull-ups
T(P, 0.3, F, 'C43.1', (55.6, -10.38), (55.6, -12.7)); V(P, 55.6, -12.7)   # U1 3V3 pin group (C35/C36/C43) via
T(P, 0.25, F, 'R63.1', (5.79, 3.85)); V(P, 5.79, 3.85)   # I2C1 pull-up R63 3V3
# band pull-ups R82.1 / R85.1: F from a new via on the x -20.05 3V3 riser along y -24.1 (south of the FLT lanes)
V(P, -20.05, -24.6); T(P, 0.2, F, (-20.05, -24.6), (-19.55, -24.1), (-7.4, -24.1), (-7.4, -27.0), (-7.78, -27.38), 'R82.1')
T(P, 0.2, F, (-7.4, -25.62), (-6.6, -26.42), (-5.8, -26.42))
# R64.1 / R66.1 3V3 via sits in the V5 band edge: F over to a via in the 3V3 plane
T(P, 0.25, F, (-8.6, -17.2), (-10.05, -17.2), (-10.35, -16.9), (-10.35, -16.55)); V(P, -10.35, -16.55)
bridge((-14.6, 9.0), (-12.9, 9.0))                        # strip between the I2C1 columns <-> GAUGE-loop piece (over I2C1_SCL In2)
# GND stitching: grid of vias (4 mm) in open F/B pour areas (stitch.py writes stitch.json from a clearance-checked grid)
import json, os
for x, y in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stitch.json'))):
    V('GND', x, y)
bridge((-14.6, -12.0), (-12.9, -12.0))                    # gauge-side piece north of the stitch via row <-> I2C1 strip
for v in ((-47.54, 13.84), (-50.49, 4.15), (44.32, -16.02)):   # GND vias for F pour pieces cut off from the stitching
    V('GND', *v)
T('GND', 0.2, F, (-50.2, -1.2), (-50.2, -1.76)); V('GND', -50.2, -1.76, dia=0.45)   # C2.2 (boxed in by VBUS / PMID) GND via
# U16 VBUS input: extra F.Cu VBUS pour vias right at the U16 input neck (PlaceRoute: >= 6 near the input)
for v in ((-49.3, -28.9), (-48.0, -29.4), (-50.9, -28.3), (-52.5, -28.3), (-54.1, -28.6)):
    V('VBUS', *v)
