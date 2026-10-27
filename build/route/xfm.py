"""Board enlargement transform (2026-10-27): 8 mm added at the north edge (125 x 65 -> 125 x 73).
A point moves north by D iff it lies north of the stepped cut line y < yc(x) with x < 33.6, or on the old north edge band (y <= -31.9).
Route modules were written in the pre-enlargement frame; rt.pt()/V()/Z() pass their explicit coordinates through xf()."""
D = 8.0
X0, Y0 = 150.0, 100.0
# local exceptions to the default cut y -17.45, where a moved part reaches further south (x ranges, cut y)
EXC = [(-26.2, -24.1, -16.3), (-12.35, -10.3, -16.0), (2.9, 4.85, -16.3), (23.6, 25.45, -16.5), (29.3, 30.2, -16.6)]
def yc(x):
    for a, b, y in EXC:
        if a <= x <= b:
            return y
    return -17.45
def moved(x, y):
    return (x < 33.6 and y < yc(x)) or y <= -31.9
def xf(p):
    x, y = p
    return (x, y - D) if moved(x, y) else (x, y)
