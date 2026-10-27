"""apply.py items.json [--keep] : replace all tracks, vias and R_* zones on the canonical board (IPC), refill, save."""
import json, os, sys
from kipy import KiCad
from kipy.board_types import Track, Via, Zone
from kipy.geometry import Vector2, PolyLine, PolyLineNode, PolygonWithHoles
from kipy.proto.board.board_types_pb2 import BoardLayer, ZoneConnectionStyle, IslandRemovalMode
NM = 1_000_000
LAY = {'F.Cu': BoardLayer.BL_F_Cu, 'In1.Cu': BoardLayer.BL_In1_Cu, 'In2.Cu': BoardLayer.BL_In2_Cu, 'B.Cu': BoardLayer.BL_B_Cu}
OX, OY = 150.0, 100.0
CONN = {'full': ZoneConnectionStyle.ZCS_FULL, 'thermal': ZoneConnectionStyle.ZCS_THERMAL, 'pth': ZoneConnectionStyle.ZCS_PTH_THERMAL}

def v2(p):
    return Vector2.from_xy(round((p[0] + OX) * NM), round((p[1] + OY) * NM))

items = json.load(open(sys.argv[1]))
kc = KiCad(socket_path=os.environ.get('KICAD_API_SOCKET', 'ipc:///tmp/e5ipc/api.sock'))
board = kc.get_board()
nets = {n.name: n for n in board.get_nets()}
c = board.begin_commit()
old = list(board.get_tracks()) + list(board.get_vias()) + [z for z in board.get_zones() if z.name.startswith('R_')]
if old:
    board.remove_items(old)
new = []
for it in items:
    if it['k'] == 't':
        t = Track(); t.start = v2(it['a']); t.end = v2(it['b']); t.width = round(it['w'] * NM)
        t.layer = LAY[it['L']]; t.net = nets[it['net']]; new.append(t)
    elif it['k'] == 'v':
        v = Via(); v.position = v2(it['p']); v.diameter = round(it['d'] * NM); v.drill_diameter = round(it['dr'] * NM)
        v.net = nets[it['net']]; new.append(v)
    else:
        z = Zone(); z.layers = [LAY[it['L']]]; z.name = it['name']; z.priority = it['prio']
        pl = PolyLine()
        for p in it['pts']:
            pl.append(PolyLineNode.from_point(v2(p)))
        pl.closed = True
        pw = PolygonWithHoles(); pw.outline = pl; z.outline = pw
        cs = z._proto.copper_settings
        if it['net']:
            cs.net.name = it['net']
        cs.connection.zone_connection = CONN[it['conn']]
        cs.connection.thermal_spokes.width.value_nm = round(it['spoke'] * NM)
        cs.connection.thermal_spokes.gap.value_nm = round(0.25 * NM)
        z.clearance = round(it['clr'] * NM); z.min_thickness = round(it['minw'] * NM)
        z.island_mode = IslandRemovalMode.IRM_AREA; z.min_island_area = round(1.0 * NM * NM)
        new.append(z)
for i in range(0, len(new), 500):
    board.create_items(new[i:i + 500])
board.push_commit(c, 'routing script')
board.refill_zones(block=True, max_poll_seconds=300)
board.save()
print('applied %d items (removed %d)' % (len(new), len(old)))
