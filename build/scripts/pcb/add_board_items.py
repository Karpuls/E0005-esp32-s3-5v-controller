"""Add E0005 placement-phase board items over IPC (kipy): antenna keep-out rule area,
U16 (U_IN) reservation markers, port / cell silkscreen.  Board-local mm (centre 150,100).

Run with the layout-placement venv python, KICAD_API_SOCKET set, from the project root:
    python build/scripts/pcb/add_board_items.py [--dry] [--replace]
--replace first deletes items this script made before (matched by text/zone name).
"""
import os
import sys

sys.path.insert(0, os.path.expanduser('~/.claude/skills/layout-placement/scripts'))
from ipc_board import load  # noqa: E402
from kipy.board_types import BoardText, BoardRectangle, Zone  # noqa: E402
from kipy.geometry import Vector2  # noqa: E402
from kipy.proto.board import board_types_pb2 as bt  # noqa: E402
from kipy.proto.board.board_types_pb2 import BoardLayer as L  # noqa: E402

OX, OY = 150.0, 100.0
NM = 1_000_000
TAG = 'E5P'          # zone names start with this, so --replace can find them


def v(x, y):
    return Vector2.from_xy(int(round((x + OX) * NM)), int(round((y + OY) * NM)))


def text(s, x, y, layer, size=1.0, thick=0.15, angle=0.0, mirror=False, width=None):
    t = BoardText()
    t.layer = layer
    t.value = s
    t.position = v(x, y)
    a = t._proto.text.attributes
    a.size.x_nm = int((width or size) * NM)
    a.size.y_nm = int(size * NM)
    a.stroke_width.value_nm = int(thick * NM)
    a.angle.value_degrees = angle
    a.mirrored = mirror
    a.horizontal_alignment = 2   # HA_CENTER
    a.vertical_alignment = 2     # VA_CENTER
    return t


def rect(x0, y0, x1, y1, layer, w=0.1):
    r = BoardRectangle()
    r.layer = layer
    r.top_left = v(x0, y0)
    r.bottom_right = v(x1, y1)
    r._proto.shape.attributes.stroke.width.value_nm = int(w * NM)
    return r


def rule_area(name, pts, layers, copper=True, vias=True, tracks=True, pads=True, footprints=False):
    z = Zone()
    p = z._proto
    p.type = bt.ZT_RULE_AREA
    p.name = name
    for ly in layers:
        p.layers.append(ly)
    ra = p.rule_area_settings
    ra.keepout_copper, ra.keepout_vias, ra.keepout_tracks = copper, vias, tracks
    ra.keepout_pads, ra.keepout_footprints = pads, footprints
    for x, y in pts:
        n = p.outline.polygons.add() if not p.outline.polygons else p.outline.polygons[0]
        pt = n.outline.nodes.add()
        pt.point.x_nm = int(round((x + OX) * NM))
        pt.point.y_nm = int(round((y + OY) * NM))
    p.outline.polygons[0].outline.closed = True
    return z


# ------------------------------------------------------------------ items
ANT = [(56.05, -24.0), (62.6, -24.0), (62.6, 24.0), (56.05, 24.0)]   # WROOM-1 antenna, all copper layers

# U16 (U_IN) reservation (SPEC 5.6.1), User.Drawings: keep area, F.Cu IN/OUT pours, B.Cu VBUS area
U16_KEEP = (-55.5, -26.6, -38.2, -19.0)          # U16 + C65, R133-R141, C66, C67, Q11, Q12
OUT_POUR = (-55.4, -31.8, -38.5, -26.6)          # V5 OUT F.Cu >= 80 mm2 (88)
IN_POUR = [(-62.0, -25.2), (-55.5, -25.2), (-55.5, -21.5), (-46.5, -21.5), (-46.5, -17.6), (-62.0, -17.6)]
#         IN F.Cu >= 80 mm2 (84): west block + south band to U16's IN bar south end
RESERVE = (-62.0, -31.8, -38.2, -17.6)           # whole reservation (keep area + pours), 23.8 x 14.2


def items():
    out = []
    out.append(rule_area(TAG + '_ANTENNA_KEEPOUT', ANT, [L.BL_F_Cu, L.BL_In1_Cu, L.BL_In2_Cu, L.BL_B_Cu]))
    D, C = L.BL_Dwgs_User, L.BL_Cmts_User
    out.append(rect(*RESERVE, C, 0.15))
    out.append(rect(*U16_KEEP, D, 0.1))
    out.append(rect(*OUT_POUR, D, 0.1))
    # IN pour outline as segments of a rectangle pair (west block + south band)
    out.append(rect(-62.0, -25.2, -55.5, -17.6, D, 0.1))
    out.append(rect(-55.5, -21.5, -46.5, -17.6, D, 0.1))
    out.append(text('U_IN keep (U16 + passives)', -46.9, -20.0, D, 0.6, 0.08))
    out.append(text('V5 OUT F.Cu pour >= 80 mm2, >= 6 vias to In2 V5', -46.9, -30.6, D, 0.6, 0.08))
    out.append(text('VBUS IN F.Cu pour >= 80 mm2', -58.7, -23.4, D, 0.6, 0.08, 90))
    out.append(text('+ B.Cu VBUS >= 100 mm2, >= 6 vias', -57.3, -21.4, D, 0.5, 0.08, 90))
    out.append(text('U_IN reservation 23.8 x 14.2 mm: no U2/L2/L1/U17 within 5 mm', -50.1, -16.9, C, 0.6, 0.08))
    out.append(text('ANTENNA KEEP-OUT all layers', 59.3, 0.0, C, 0.8, 0.1, 90))

    S, B = L.BL_F_SilkS, L.BL_B_SilkS
    # ports: "5V" + port number + E0001/E0002 next to each connector (E0003's text positions)
    for j, (x1, x2) in {'J1': (-27.3, -25.8), 'J2': (-12.8, -11.3), 'J3': (1.7, 3.2),
                        'J4': (16.2, 17.7)}.items():
        out.append(text('5V', x1, -27.9, S, 1.0, 0.15, 90, width=0.75))
        out.append(text(j + ' E0001', x2, -28.3, S, 1.0, 0.15, 90, width=0.75))
    out.append(text('5V', 32.15, -27.9, S, 1.0, 0.15, 90, width=0.75))
    out.append(text('J5 E0002', 33.65, -28.3, S, 1.0, 0.15, 90, width=0.75))
    # cell polarity, top (E0003 positions; CELL2 + moved off the 3V3 buck)
    out.append(text('CELL1 -', -28.55, -9.45, S))
    out.append(text('CELL2 +', -35.15, 9.9, S))
    out.append(text('CELL1 +', 36.15, -16.05, S))
    out.append(text('CELL2 -', 36.15, 16.05, S))
    # cell polarity, bottom (mirrored), board label
    out.append(text('CELL1 -', -34.15, -16.05, B, mirror=True))
    out.append(text('CELL2 +', -34.15, 16.05, B, mirror=True))
    out.append(text('CELL1 +', 36.15, -16.05, B, mirror=True))
    out.append(text('CELL2 -', 36.15, 16.05, B, mirror=True))
    out.append(text('2 x 21700 P50B', -2.0, -28.6, B, 1.2, 0.15, mirror=True))
    out.append(text('E0005 ESP32-S3 5V CONTROLLER rev A', -2.0, 28.6, B, 1.2, 0.15, mirror=True))
    # edge labels (E0003)
    for s, x, y, a in (('PWR', -41.0, 26.7, 0), ('SW1', -23.0, 26.7, 0),
                       ('SW2', -13.0, 26.7, 0), ('SW3', -3.0, 26.7, 0), ('SW4', 7.0, 26.7, 0),
                       ('EYESPI LCD', 30.0, 19.4, 0), ('BOOT', 44.5, 26.0, 0), ('RESET', 50.8, 26.0, 0)):
        out.append(text(s, x, y, S, 1.0, 0.15, a))
    return out


def main():
    b = load(os.path.abspath('E0005_controller.kicad_pcb'))
    board = b['board']
    new = items()
    if '--dry' in sys.argv:
        print(len(new), 'items (dry run)')
        return
    mine = {'CELL1 -', 'CELL2 +', 'CELL1 +', 'CELL2 -', '5V', '2 x 21700 P50B', 'USB-C', 'PWR', 'SW1', 'SW2',
            'SW3', 'SW4', 'EYESPI LCD', 'BOOT', 'RESET'}
    commit = board.begin_commit()
    if '--replace' in sys.argv:
        old = [t for t in board.get_text() if isinstance(t, BoardText) and
               (t.value in mine or t.value.startswith(('J1 E0', 'J2 E0', 'J3 E0', 'J4 E0', 'J5 E0', 'U_IN',
                                                        'V5 OUT', 'VBUS IN', '+ B.Cu', 'ANTENNA', 'E0005 ESP32')))]
        old += [z for z in board.get_zones() if z.name.startswith(TAG)]
        old += [s for s in board.get_shapes() if s.layer in (L.BL_Dwgs_User, L.BL_Cmts_User)]
        if old:
            board.remove_items(old)
        print('removed', len(old))
    made = board.create_items(new)
    board.push_commit(commit, 'E0005 placement markers')
    print('created', len(made))
    if '--save' in sys.argv:
        board.save()
        print('saved')


if __name__ == '__main__':
    main()
