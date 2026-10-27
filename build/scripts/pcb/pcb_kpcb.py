"""E0003 board-generation (adapted from E0002) helpers (pcbnew-free).

Loads KiCad library footprints, places them (top or bottom, any rotation),
assigns nets from the schematic netlist and serialises a KiCad 10 .kicad_pcb.
Bottom-side placement follows KiCad's own flip: local (x, y) -> (x, -y),
local angles negated, F.* <-> B.* layers, text mirrored.
"""
import math
import os
import uuid as _uuid

from pcb_sexp import parse, dump, Sym, q

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
KROOT = '/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/share/kicad'
BOARD = os.environ.get('PCB_OUT') or os.path.join(PROJ, 'E0005_controller.kicad_pcb')
NETLIST = os.path.join(PROJ, 'build', 'layout', 'current.net')
NS = _uuid.UUID('6f1b5e0a-2f2b-4b38-9a1e-e0005b0a4d00')

# Board centre on the page; all layout coordinates are relative to it.
OX, OY = 150.0, 100.0


def uid(*parts):
    return str(_uuid.uuid5(NS, '/'.join(str(p) for p in parts)))


def fnum(v):
    v = round(float(v), 6)
    if v == 0:
        v = 0.0
    s = ('%.6f' % v).rstrip('0').rstrip('.')
    return Sym(s if s not in ('-0', '') else '0')


def rot(x, y, a_deg):
    """KiCad rotation (screen, y down): CCW-positive angle."""
    a = math.radians(a_deg)
    c, s = math.cos(a), math.sin(a)
    return x * c + y * s, -x * s + y * c


# ---------------------------------------------------------------- netlist
def load_netlist(path=NETLIST):
    t = parse(open(path).read())
    comps, nets = {}, {}
    for c in [x for x in t if isinstance(x, list) and x[0] == 'components'][0][1:]:
        d = {}
        for x in c[1:]:
            if isinstance(x, list):
                d.setdefault(x[0], x)
        ref = d['ref'][1]
        fields = []
        for f in d.get('fields', ['fields'])[1:]:
            name = f[1][1]
            val = f[2] if len(f) > 2 else ''
            fields.append((name, val))
        props = {}
        for x in c[1:]:
            if isinstance(x, list) and x[0] == 'property':
                nm = x[1][1]
                props[nm] = x[2][1] if len(x) > 2 else ''
        sp = d.get('sheetpath')
        spt = [y for y in sp[1:] if y[0] == 'tstamps'][0][1] if sp else '/'
        spn = [y for y in sp[1:] if y[0] == 'names'][0][1] if sp else '/'
        comps[ref] = dict(ref=ref, value=d['value'][1], footprint=d['footprint'][1],
                          tstamp=d['tstamps'][1], fields=fields, props=props,
                          sheetpath=spt, sheetname=spn.strip('/') or '/',
                          sheetfile=props.get('Sheetfile', 'E0005_controller.kicad_sch'),
                          description=d['description'][1] if 'description' in d else '')
    for n in [x for x in t if isinstance(x, list) and x[0] == 'nets'][0][1:]:
        name = [x for x in n if isinstance(x, list) and x[0] == 'name'][0][1]
        for x in n:
            if isinstance(x, list) and x[0] == 'node':
                r = [y for y in x if isinstance(y, list) and y[0] == 'ref'][0][1]
                p = [y for y in x if isinstance(y, list) and y[0] == 'pin'][0][1]
                nets[(r, p)] = name
    return comps, nets


# ---------------------------------------------------------------- footprints
_fp_cache = {}


def fp_file(libid):
    lib, name = libid.split(':')
    if lib in ('E0005_mech', 'E0005'):
        return os.path.join(PROJ, 'lib', lib + '.pretty', name + '.kicad_mod')
    local = os.path.join(PROJ, 'lib', lib + '.pretty', name + '.kicad_mod')
    if os.path.exists(local):
        return local
    return os.path.join(KROOT, 'footprints', lib + '.pretty', name + '.kicad_mod')


def load_fp(libid):
    if libid not in _fp_cache:
        _fp_cache[libid] = parse(open(fp_file(libid)).read())
    return _fp_cache[libid]


def _copy(e):
    return [_copy(x) for x in e] if isinstance(e, list) else e


def flip_layer(s):
    if isinstance(s, str) and len(s) > 2 and s[1] == '.' and s[0] in 'FB':
        return ('B' if s[0] == 'F' else 'F') + s[1:]
    return s


COORD_KEYS = ('at', 'start', 'end', 'mid', 'center', 'xy')


def _flip_tree(e, in_model=False):
    """Mirror a footprint subtree to the bottom side (local coords)."""
    if not isinstance(e, list) or not e:
        return
    head = e[0]
    if head == 'model':
        return
    if head in COORD_KEYS and len(e) >= 3 and not isinstance(e[1], list):
        e[2] = fnum(-float(e[2]))
        if head == 'at' and len(e) >= 4 and not isinstance(e[3], list):
            e[3] = fnum(-float(e[3]))
        return
    if head in ('layer', 'layers'):
        for i in range(1, len(e)):
            if isinstance(e[i], str):
                e[i] = type(e[i])(flip_layer(e[i])) if isinstance(e[i], Sym) else flip_layer(e[i])
        return
    for x in e[1:]:
        _flip_tree(x)


def _find(e, key):
    for x in e:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def _findall(e, key):
    return [x for x in e if isinstance(x, list) and x and x[0] == key]


class Part:
    def __init__(self, ref, comp, x, y, a=0.0, side='F', nets=None):
        self.ref, self.comp = ref, comp
        self.x, self.y, self.a, self.side = x, y, a, side
        self.libid = comp['footprint']
        self.nets = nets or {}
        self.drop_pads = []          # predicates (pad sexp) -> drop
        self.locked = False
        self.ref_silk = 'lib'        # 'lib' = library position, None = hidden, (dx, dy, vertical) = board offset

    # absolute (page) coordinates of a local point (after flip)
    def to_abs(self, lx, ly):
        dx, dy = rot(lx, ly, self.a)
        return OX + self.x + dx, OY + self.y + dy

    def build(self):
        src = _copy(load_fp(self.libid))
        body = src[2:]
        if self.side == 'B':
            for item in body:
                _flip_tree(item)
        out = [Sym('footprint'), q_str(self.libid)]
        out.append([Sym('layer'), 'B.Cu' if self.side == 'B' else 'F.Cu'])
        out.append([Sym('uuid'), uid('fp', self.ref)])
        at = [Sym('at'), fnum(OX + self.x), fnum(OY + self.y)]
        if self.a:
            at.append(fnum(self.a))
        out.append(at)
        if self.locked:
            out.append([Sym('locked'), Sym('yes')])
        comp = self.comp
        skip = ('version', 'generator', 'generator_version', 'layer', 'uuid', 'attr', 'embedded_fonts')
        props_done = set()
        attr = _find(body, 'attr')
        items = []
        pad_n = 0
        for item in body:
            if not isinstance(item, list):
                continue
            h = item[0]
            if h in skip:
                continue
            if h == 'property':
                name = item[1]
                if name == 'Reference':
                    item[2] = self.ref
                elif name == 'Value':
                    item[2] = comp['value']
                elif name == 'Datasheet':
                    item[2] = dict(comp['fields']).get('Datasheet', '') or ''
                elif name == 'Description':
                    item[2] = dict(comp['fields']).get('Description', '') or ''
                props_done.add(name)
                self._abs_angle(item)
                if name == 'Reference' and self.ref_silk != 'lib':
                    self._set_ref(item)
                self._mirror_text(item)
                self._fix_uuid(item, 'prop', name)
                items.append(item)
                continue
            if h == 'fp_text':
                self._abs_angle(item)
                self._mirror_text(item)
                self._fix_uuid(item, 'txt', len(items))
                items.append(item)
                continue
            if h == 'pad':
                if any(p(item) for p in self.drop_pads):
                    continue
                pad_n += 1
                self._abs_angle(item, pad=True)
                num = item[1]
                net = self.nets.get((self.ref, num))
                # insert net after layers
                li = [i for i, x in enumerate(item) if isinstance(x, list) and x and x[0] == 'layers']
                item[:] = [x for x in item if not (isinstance(x, list) and x and x[0] == 'net')]
                if net and num != '':
                    li = [i for i, x in enumerate(item) if isinstance(x, list) and x and x[0] == 'layers']
                    item.insert(li[0] + 1, [Sym('net'), net])
                self._fix_uuid(item, 'pad', pad_n)
                items.append(item)
                continue
            if h == 'zone':
                # footprint zones are stored in absolute board coordinates
                pg = _find(item, 'polygon')
                for xy in _find(pg, 'pts')[1:]:
                    ax, ay = self.to_abs(float(xy[1]), float(xy[2]))
                    xy[1], xy[2] = fnum(ax), fnum(ay)
            self._fix_uuid(item, 'g', len(items))
            items.append(item)
        # extra fields as hidden properties (parity: field match)
        extra = []
        for name, val in comp['fields']:
            if name in ('Footprint', 'Sheetname', 'Sheetfile') or name in props_done:
                continue
            extra.append([Sym('property'), name, val or '',
                          [Sym('at'), fnum(0), fnum(0), fnum(self.a)],
                          [Sym('layer'), 'B.Fab' if self.side == 'B' else 'F.Fab'],
                          [Sym('hide'), Sym('yes')],
                          [Sym('uuid'), uid('xprop', self.ref, name)],
                          [Sym('effects'), [Sym('font'), [Sym('size'), fnum(1), fnum(1)], [Sym('thickness'), fnum(0.15)]]]
                          + ([[Sym('justify'), Sym('mirror')]] if self.side == 'B' else [])])
        props = [x for x in items if x[0] == 'property']
        rest = [x for x in items if x[0] != 'property']
        out += props + extra
        if comp.get('board_only'):
            pass
        else:
            out.append([Sym('path'), comp.get('sheetpath', '/') + comp['tstamp']])
            out.append([Sym('sheetname'), comp.get('sheetname', '/')])
            out.append([Sym('sheetfile'), comp.get('sheetfile', 'E0005_controller.kicad_sch')])
        a = [Sym('attr')]
        if attr:
            a += [x for x in attr[1:] if x not in ('exclude_from_bom', 'dnp')]
        else:
            a += [Sym('smd')]
        p = comp['props']
        if 'exclude_from_bom' in p and Sym('exclude_from_bom') not in a:
            a.append(Sym('exclude_from_bom'))
        if 'exclude_from_pos_files' in p and Sym('exclude_from_pos_files') not in a:
            a.append(Sym('exclude_from_pos_files'))
        if 'dnp' in p:
            a.append(Sym('dnp'))
        if len(a) == 1:
            a.append(Sym('smd'))
        out.append(a)
        out += rest
        return out

    def _abs_angle(self, item, pad=False):
        at = _find(item, 'at')
        if at is None:
            return
        la = float(at[3]) if len(at) >= 4 and not isinstance(at[3], list) else 0.0
        aa = (la + self.a) % 360.0
        if aa > 180:
            aa -= 360
        if len(at) >= 4:
            at[3] = fnum(aa)
        elif aa:
            at.append(fnum(aa))

    def _set_ref(self, item):
        item[:] = [x for x in item if not (isinstance(x, list) and x and x[0] == 'hide')]
        if self.ref_silk is None:
            item.insert(4, [Sym('hide'), Sym('yes')])
            return
        dx, dy, vert = self.ref_silk
        lx, ly = rot(dx, dy, -self.a)
        at = _find(item, 'at')
        at[1:] = [fnum(lx), fnum(ly), fnum(90 if vert else 0)]
        eff = _find(item, 'effects')
        font = _find(eff, 'font')
        font[1:] = [[Sym('size'), fnum(1), fnum(1)], [Sym('thickness'), fnum(0.15)]]
        eff[:] = [x for x in eff if not (isinstance(x, list) and x and x[0] == 'justify')]

    def _mirror_text(self, item):
        if self.side != 'B':
            return
        eff = _find(item, 'effects')
        if eff is None:
            return
        j = _find(eff, 'justify')
        if j is None:
            eff.append([Sym('justify'), Sym('mirror')])
        elif 'mirror' not in j:
            j.append(Sym('mirror'))

    def _fix_uuid(self, item, kind, n):
        u = _find(item, 'uuid')
        if u is not None:
            u[1] = uid(self.ref, kind, n)

    # ---- geometry for the router / checks
    def pads(self):
        """List of dicts: num, net, shape, cx, cy (abs page), w, h, ang (abs), layers, drill."""
        src = _copy(load_fp(self.libid))
        out = []
        for item in src[2:]:
            if not (isinstance(item, list) and item and item[0] == 'pad'):
                continue
            if any(p(item) for p in self.drop_pads):
                continue
            if self.side == 'B':
                _flip_tree(item)
            num = item[1]
            ptype = str(item[2])
            shape = str(item[3])
            at = _find(item, 'at')
            lx, ly = float(at[1]), float(at[2])
            la = float(at[3]) if len(at) >= 4 else 0.0
            sz = _find(item, 'size')
            w, h = float(sz[1]), float(sz[2])
            if shape == 'custom':
                # bounding box of primitives around the anchor
                xs, ys = [-w / 2, w / 2], [-h / 2, h / 2]
                prim = _find(item, 'primitives')
                for pr in prim[1:] if prim else []:
                    if pr[0] == 'gr_circle':
                        c = _find(pr, 'center'); e = _find(pr, 'end')
                        r = math.hypot(float(e[1]) - float(c[1]), float(e[2]) - float(c[2]))
                        xs += [float(c[1]) - r, float(c[1]) + r]; ys += [float(c[2]) - r, float(c[2]) + r]
                    elif pr[0] == 'gr_poly':
                        for p in _find(pr, 'pts')[1:]:
                            xs.append(float(p[1])); ys.append(float(p[2]))
                    elif pr[0] in ('gr_line', 'gr_rect'):
                        for k in ('start', 'end'):
                            p = _find(pr, k); xs.append(float(p[1])); ys.append(float(p[2]))
                # re-centre
                cxo, cyo = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
                dx, dy = rot(cxo, cyo, la)
                lx += dx; ly += dy
                w, h = max(xs) - min(xs), max(ys) - min(ys)
                shape = 'rect'
            layers = [str(x) for x in _find(item, 'layers')[1:]]
            dr = _find(item, 'drill')
            drill = None
            if dr is not None:
                vals = [float(x) for x in dr[1:] if not isinstance(x, list) and str(x) != 'oval']
                drill = max(vals) if vals else None
            rr = _find(item, 'roundrect_rratio')
            ax, ay = self.to_abs(lx, ly)
            out.append(dict(ref=self.ref, num=num, net=self.nets.get((self.ref, num)) if num else None,
                            type=ptype, shape=shape, cx=ax, cy=ay, w=w, h=h,
                            ang=(la + self.a) % 360, layers=layers, drill=drill,
                            rr=float(rr[1]) if rr else 0.0))
        return out

    def courtyard(self):
        """Absolute bbox (minx, miny, maxx, maxy) of the courtyard on our side, or None."""
        src = _copy(load_fp(self.libid))
        pts = []
        lay = 'F.CrtYd'
        for item in src[2:]:
            if not isinstance(item, list):
                continue
            l = _find(item, 'layer')
            if l is None or l[1] != lay:
                continue
            for k in ('start', 'end', 'mid', 'center'):
                p = _find(item, k)
                if p is not None:
                    pts.append((float(p[1]), float(p[2])))
            pp = _find(item, 'pts')
            if pp:
                pts += [(float(p[1]), float(p[2])) for p in pp[1:]]
        if not pts:
            return None
        if self.side == 'B':
            pts = [(x, -y) for x, y in pts]
        ap = [self.to_abs(x, y) for x, y in pts]
        xs = [p[0] for p in ap]; ys = [p[1] for p in ap]
        return min(xs), min(ys), max(xs), max(ys)


def q_str(s):
    return s


# ---------------------------------------------------------------- board items
def seg(x1, y1, x2, y2, w, layer, net, tag, locked=False):
    return [Sym('segment')] + ([[Sym('locked'), Sym('yes')]] if locked else []) + [[Sym('start'), fnum(x1), fnum(y1)], [Sym('end'), fnum(x2), fnum(y2)],
            [Sym('width'), fnum(w)], [Sym('layer'), layer], [Sym('net'), net],
            [Sym('uuid'), uid('seg', tag)]]


def via(x, y, net, tag, size=0.6, drill=0.3, locked=False):
    v = [Sym('via')] + ([[Sym('locked'), Sym('yes')]] if locked else []) + [
        [Sym('at'), fnum(x), fnum(y)], [Sym('size'), fnum(size)], [Sym('drill'), fnum(drill)],
        [Sym('layers'), 'F.Cu', 'B.Cu'], [Sym('net'), net], [Sym('uuid'), uid('via', tag)]]
    return v


def gr_line(x1, y1, x2, y2, layer, w, tag):
    return [Sym('gr_line'), [Sym('start'), fnum(x1), fnum(y1)], [Sym('end'), fnum(x2), fnum(y2)],
            [Sym('stroke'), [Sym('width'), fnum(w)], [Sym('type'), Sym('solid')]],
            [Sym('layer'), layer], [Sym('uuid'), uid('gr', tag)]]


def gr_arc(s, m, e, layer, w, tag):
    return [Sym('gr_arc'), [Sym('start'), fnum(s[0]), fnum(s[1])], [Sym('mid'), fnum(m[0]), fnum(m[1])],
            [Sym('end'), fnum(e[0]), fnum(e[1])],
            [Sym('stroke'), [Sym('width'), fnum(w)], [Sym('type'), Sym('solid')]],
            [Sym('layer'), layer], [Sym('uuid'), uid('gr', tag)]]


def gr_text(txt, x, y, layer, size, thick, tag, angle=0, mirror=False, justify=None, width=None):
    eff = [Sym('effects'), [Sym('font'), [Sym('size'), fnum(size), fnum(width or size)], [Sym('thickness'), fnum(thick)]]]
    j = []
    if justify:
        j.append(Sym(justify))
    if mirror:
        j.append(Sym('mirror'))
    if j:
        eff.append([Sym('justify')] + j)
    return [Sym('gr_text'), txt, [Sym('at'), fnum(x), fnum(y), fnum(angle)], [Sym('layer'), layer],
            [Sym('uuid'), uid('txt', tag)], eff]


def zone(net, layers, pts, tag, priority=0, clearance=0.2, min_th=0.2, thermal_gap=0.3,
         spoke=0.4, connect=None, name=None, island='always', fill_holes=None, keepout=None,
         layer_names=None):
    z = [Sym('zone')]
    if keepout is None:
        z.append([Sym('net'), net])
    if len(layers) == 1:
        z.append([Sym('layer'), layers[0]])
    else:
        z.append([Sym('layers')] + list(layers))
    z.append([Sym('uuid'), uid('zone', tag)])
    if name:
        z.append([Sym('name'), name])
    z.append([Sym('hatch'), Sym('edge'), fnum(0.5)])
    if priority:
        z.append([Sym('priority'), Sym(str(priority))])
    if keepout is None:
        cs = [Sym('connect_pads')]
        if connect:
            cs.append(Sym(connect))
        cs.append([Sym('clearance'), fnum(clearance)])
        z.append(cs)
    else:
        z.append([Sym('connect_pads'), [Sym('clearance'), fnum(0)]])
    z.append([Sym('min_thickness'), fnum(min_th)])
    z.append([Sym('filled_areas_thickness'), Sym('no')])
    if keepout is not None:
        k = [Sym('keepout')]
        for key in ('tracks', 'vias', 'pads', 'copperpour', 'footprints'):
            k.append([Sym(key), Sym('not_allowed' if key in keepout else 'allowed')])
        z.append(k)
        z.append([Sym('placement'), [Sym('enabled'), Sym('no')], [Sym('sheetname'), '']])
    fs = [Sym('fill'), Sym('yes'), [Sym('thermal_gap'), fnum(thermal_gap)],
          [Sym('thermal_bridge_width'), fnum(spoke)]]
    if keepout is None:
        fs.append([Sym('island_removal_mode'), Sym({'always': '0', 'never': '1', 'area': '2'}[island])])
        if island == 'area':
            fs.append([Sym('island_area_min'), fnum(4)])
    if keepout is None:
        z.append(fs)
    z.append([Sym('polygon'), [Sym('pts')] + [[Sym('xy'), fnum(x), fnum(y)] for x, y in pts]])
    return z


LAYERS_HDR = '''	(layers
		(0 "F.Cu" signal)
		(4 "In1.Cu" power)
		(6 "In2.Cu" power)
		(2 "B.Cu" signal)
		(9 "F.Adhes" user "F.Adhesive")
		(11 "B.Adhes" user "B.Adhesive")
		(13 "F.Paste" user)
		(15 "B.Paste" user)
		(5 "F.SilkS" user "F.Silkscreen")
		(7 "B.SilkS" user "B.Silkscreen")
		(1 "F.Mask" user)
		(3 "B.Mask" user)
		(17 "Dwgs.User" user "User.Drawings")
		(19 "Cmts.User" user "User.Comments")
		(21 "Eco1.User" user "User.Eco1")
		(23 "Eco2.User" user "User.Eco2")
		(25 "Edge.Cuts" user)
		(27 "Margin" user)
		(31 "F.CrtYd" user "F.Courtyard")
		(29 "B.CrtYd" user "B.Courtyard")
		(35 "F.Fab" user)
		(33 "B.Fab" user)
	)
	(setup
		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "prepreg") (thickness 0.0994) (material "FR4") (epsilon_r 4.1) (loss_tangent 0.02))
			(layer "In1.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 2" (type "core") (thickness 1.265) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
			(layer "In2.Cu" (type "copper") (thickness 0.0152))
			(layer "dielectric 3" (type "prepreg") (thickness 0.0994) (material "FR4") (epsilon_r 4.1) (loss_tangent 0.02))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
		(pad_to_mask_clearance 0)
		(allow_soldermask_bridges_in_footprints no)
		(tenting
			(front yes)
			(back yes)
		)
		(pcbplotparams
			(layerselection 0x00000000_00000000_55555555_5755f5ff)
			(plot_on_all_layers_selection 0x00000000_00000000_00000000_00000000)
			(usegerberextensions no)
			(usegerberattributes yes)
			(usegerberadvancedattributes yes)
			(creategerberjobfile yes)
			(svgprecision 4)
			(plotframeref no)
			(mode 1)
			(useauxorigin no)
			(outputformat 1)
			(mirror no)
			(drillshape 1)
			(scaleselection 1)
			(outputdirectory "")
		)
	)
'''


def write_board(path, items, title='E0003 ESP32 control box mainboard', rev='A', date='2026-10-11'):
    out = ['(kicad_pcb\n\t(version 20260206)\n\t(generator "e0005_gen_pcb")\n\t(generator_version "10.0")\n'
           '\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper "A4")\n']
    out.append('\t(title_block\n\t\t(title %s)\n\t\t(date %s)\n\t\t(rev %s)\n'
               '\t\t(comment 1 "4 layers 1.6 mm, 1 oz outer / 0.5 oz inner")\n\t)\n'
               % (q(title), q(date), q(rev)))
    out.append(LAYERS_HDR)
    for it in items:
        out.append('\t' + dump(it, 1) + '\n')
    out.append(')\n')
    tmp = path + '.tmp'
    with open(tmp, 'w') as f:
        f.write(''.join(out))
    os.replace(tmp, path)
