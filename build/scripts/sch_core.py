"""Hierarchical KiCad 10 schematic generator core (E0005), same style as E0001/E0002.

Each Sheet collects symbols, wires, labels and graphics in grid units (G = 2.54 mm).
Net labels are written as local labels unless the net name is used on more than one
sheet, in which case they become global labels. Deterministic uuid5 UUIDs.
"""
import os, sys, uuid, math
sys.path.insert(0, os.path.dirname(__file__))
from sexp import Sym as S, dump, find, findall
import symlib

G = 2.54
NS = uuid.UUID('6f0a3c1e-2b7d-4f7e-9a51-0e0005c0b0c0')

def U(*parts):
    return str(uuid.uuid5(NS, '/'.join(str(p) for p in parts)))

POWER_NETS = {'GND', '+3V3', 'VSYS', 'VBUS', 'BAT+'}
GND_NETS = {'GND'}

C_PWR = (190, 0, 90)
C_BAT = (0, 120, 60)
C_MCU = (0, 84, 200)
C_PORT = (205, 100, 0)
C_UI = (110, 80, 40)

lib_cache = {}

def libsym(lib_id):
    if lib_id not in lib_cache:
        lib, name = lib_id.split(':', 1)
        lib_cache[lib_id] = symlib.load(lib, name)
    return lib_cache[lib_id]

def font(size=1.27, bold=False, color=None):
    f = [S('font'), [S('size'), size, size]]
    if bold:
        f += [[S('thickness'), round(size * 0.2, 3)], [S('bold'), S('yes')]]
    if color:
        f.append([S('color'), color[0], color[1], color[2], 1])
    return f

def effects(size=1.27, justify=None, hide=False, bold=False, color=None):
    e = [S('effects'), font(size, bold, color)]
    if justify:
        e.append([S('justify')] + [S(j) for j in justify.split()])
    if hide:
        e.append([S('hide'), S('yes')])
    return e

def prop(name, value, x, y, rot=0, hide=False, justify=None, size=1.27):
    return [S('property'), name, value, [S('at'), x, y, rot], effects(size, justify, hide)]

def xform(px, py, x, y, rot, mirror):
    if mirror == 'y':
        px = -px
    elif mirror == 'x':
        py = -py
    a = math.radians(rot)
    xr = px * math.cos(a) - py * math.sin(a)
    yr = px * math.sin(a) + py * math.cos(a)
    return (round(x + xr, 4), round(y - yr, 4))

SIDE = {(1, 0): 'right', (-1, 0): 'left', (0, -1): 'up', (0, 1): 'down'}


class Sheet:
    def __init__(self, name, fname, paper='A3', page=2, size=None):
        self.name, self.fname, self.paper, self.page, self.size = name, fname, paper, page, size
        self.uuid = U('sheet', name)
        self.symbols, self.items, self.labels = [], [], []
        self.inst = {}
        self.pwr = 0
        self.stubbed = set()

    # ------------------------------------------------------------- placement
    def place(self, lib_id, ref, value, x, y, rot=0, mirror=None, fp='', desc='',
              refpos=None, valpos=None, extra=None, dnp=False, in_bom=True, in_pos=True, hide_value=False,
              alts=None, ds=None):
        X, Y = x * G, y * G
        sym = libsym(lib_id)
        pr = {p[1]: p for p in findall(sym, 'property')}
        if not fp and 'Footprint' in pr:
            fp = pr['Footprint'][2]
        if ds is None:
            ds = pr['Datasheet'][2] if 'Datasheet' in pr else '~'
        if not desc and 'Description' in pr:
            desc = pr['Description'][2]
        ispower = ref.startswith('#')
        e = [S('symbol'), [S('lib_id'), lib_id], [S('at'), X, Y, rot]]
        if mirror:
            e.append([S('mirror'), S(mirror)])
        e += [[S('unit'), 1], [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes' if in_bom else 'no')],
              [S('on_board'), S('yes')], [S('in_pos_files'), S('yes' if in_pos else 'no')],
              [S('dnp'), S('yes' if dnp else 'no')], [S('uuid'), U('sym', ref)]]
        rx, ry, rj = refpos if refpos else (x, y - 2, None)
        vx, vy, vj = valpos if valpos else (x, y + 2, None)
        if rot in (90, 180, 270):
            rj = vj = None
        fa = 90 if rot in (90, 270) else 0
        e.append(prop('Reference', ref, rx * G, ry * G, fa, hide=ispower, justify=rj))
        e.append(prop('Value', value, vx * G, vy * G, fa, hide=hide_value, justify=vj))
        e.append(prop('Footprint', fp, X, Y, 0, hide=True))
        e.append(prop('Datasheet', ds, X, Y, 0, hide=True))
        e.append(prop('Description', desc, X, Y, 0, hide=True))
        for k, v in (extra or {}).items():
            e.append(prop(k, v, X, Y, 0, hide=True))
        for p in symlib.pins(sym):
            pe = [S('pin'), p['number'], [S('uuid'), U('pin', ref, p['number'])]]
            if alts and p['number'] in alts:
                pe.append([S('alternate'), alts[p['number']]])
            e.append(pe)
        e.append([S('instances'), [S('project'), PROJECT,
                                   [S('path'), '/' + ROOT[0] + '/' + self.uuid,
                                    [S('reference'), ref], [S('unit'), 1]]]])
        self.symbols.append(e)
        self.inst[ref] = dict(x=X, y=Y, rot=rot, mirror=mirror, sym=sym)
        return e

    def _pin(self, ref, num):
        d = self.inst[ref]
        for p in symlib.pins(d['sym']):
            if p['number'] == num:
                return p, d
        raise KeyError(ref + '.' + num)

    def pin(self, ref, num):
        p, d = self._pin(ref, num)
        return xform(p['x'], p['y'], d['x'], d['y'], d['rot'], d['mirror'])

    def outward(self, ref, num):
        p, d = self._pin(ref, num)
        a = math.radians(p['angle'])
        inner = xform(p['x'] + math.cos(a), p['y'] + math.sin(a), d['x'], d['y'], d['rot'], d['mirror'])
        outer = xform(p['x'], p['y'], d['x'], d['y'], d['rot'], d['mirror'])
        return (round(outer[0] - inner[0]), round(outer[1] - inner[1]))

    # ------------------------------------------------------------- drawing
    def wire(self, *pts):
        for a, b in zip(pts[:-1], pts[1:]):
            self.items.append([S('wire'), [S('pts'), [S('xy'), a[0], a[1]], [S('xy'), b[0], b[1]]],
                               [S('stroke'), [S('width'), 0], [S('type'), S('default')]],
                               [S('uuid'), U(self.name, 'wire', a, b)]])

    def label(self, name, p, side='right'):
        self.labels.append((name, p, side))

    def junction(self, p):
        self.items.append([S('junction'), [S('at'), p[0], p[1]], [S('diameter'), 0], [S('color'), 0, 0, 0, 0],
                           [S('uuid'), U(self.name, 'junc', p)]])

    def noconnect(self, p):
        self.items.append([S('no_connect'), [S('at'), p[0], p[1]], [S('uuid'), U(self.name, 'nc', p)]])

    def power(self, net, p, flip=False):
        self.pwr += 1
        ref = '#PWR%d%03d' % (self.page, self.pwr)
        if net in GND_NETS:
            self.place('power:GND', ref, net, p[0] / G, p[1] / G, 0,
                       valpos=(p[0] / G, p[1] / G + 1.5, None))
        else:
            self.place('power:VDD', ref, net, p[0] / G, p[1] / G, 180 if flip else 0,
                       valpos=(p[0] / G, p[1] / G + (1.4 if flip else -1.4), None))

    def flag(self, net, x, y):
        self.pwr += 1
        p = (x * G, y * G)
        self.place('power:PWR_FLAG', '#FLG%d%03d' % (self.page, self.pwr), 'PWR_FLAG', x, y, 0,
                   valpos=(x, y - 1.5, None))
        q = (p[0], p[1] + G)
        self.wire(p, q)
        if net in GND_NETS:
            self.power(net, q)
        elif net in POWER_NETS:
            self.power(net, q, flip=True)
        else:
            self.label(net, q, 'down')

    def net(self, ref, num, name, L=1):
        """Stub of L grid units from a pin, ending in a label, power symbol or no-connect (name None)."""
        p = self.pin(ref, num)
        if p in self.stubbed:          # stacked pins share one connection point
            return p
        self.stubbed.add(p)
        if name is None:
            self.noconnect(p)
            return p
        d = self.outward(ref, num)
        q = (round(p[0] + d[0] * L * G, 4), round(p[1] + d[1] * L * G, 4))
        self.wire(p, q)
        if name in GND_NETS:
            self.power(name, q)
        elif name in POWER_NETS:
            self.power(name, q, flip=(d == (0, 1)))
        else:
            self.label(name, q, SIDE[d])
        return q

    def tie(self, ref, nums, name, L=2):
        """Join several same-side pins with a bus wire and one power symbol / label."""
        pts = [self.pin(ref, n) for n in nums]
        d = self.outward(ref, nums[0])
        ends = []
        for p in pts:
            q = (round(p[0] + d[0] * L * G, 4), round(p[1] + d[1] * L * G, 4))
            self.wire(p, q)
            self.stubbed.add(p)
            ends.append(q)
        ends.sort(key=lambda q: (q[1], q[0]))
        for a, b in zip(ends[:-1], ends[1:]):
            self.wire(a, b)
        for q in ends[1:-1]:
            self.junction(q)
        end = ends[-1]
        if name in GND_NETS:
            self.power(name, end)
        elif name in POWER_NETS:
            self.power(name, ends[0])
        else:
            self.label(name, end, SIDE[d])

    def nets(self, ref, mapping, L=1):
        for num, name in mapping.items():
            self.net(ref, num, name, L)

    def rect(self, x1, y1, x2, y2, color, title):
        self.items.append([S('rectangle'), [S('start'), x1 * G, y1 * G], [S('end'), x2 * G, y2 * G],
                           [S('stroke'), [S('width'), 0.3], [S('type'), S('dash')],
                            [S('color'), color[0], color[1], color[2], 1]],
                           [S('fill'), [S('type'), S('color')], [S('color'), color[0], color[1], color[2], 0.05]],
                           [S('uuid'), U(self.name, 'rect', title)]])
        self.text(title, x1 + 1, y1 + 1.8, size=2.0, bold=True, color=color)

    def text(self, s, x, y, size=1.27, bold=False, color=None):
        self.items.append([S('text'), s, [S('exclude_from_sim'), S('no')], [S('at'), x * G, y * G, 0],
                           effects(size, 'left bottom', bold=bold, color=color), [S('uuid'), U(self.name, 'text', s, x, y)]])

    def notes(self, lines, x, y, color=None):
        for i, s in enumerate(lines):
            self.text(s, x, y + i, color=color)


PROJECT = 'E0005_controller'
ROOT = [U('root')]


# Net names kept global even if used on one sheet only (keeps board net names stable).
FORCE_GLOBAL = set()


def emit_labels(sheets):
    used = {}
    for sh in sheets:
        for name, _, _ in sh.labels:
            used.setdefault(name, set()).add(sh.name)
    for sh in sheets:
        for name, p, side in sh.labels:
            rot = {'right': 0, 'left': 180, 'up': 90, 'down': 270}[side]
            just = {'right': 'left', 'left': 'right', 'up': 'left', 'down': 'right'}[side]
            if len(used[name]) > 1 or name in FORCE_GLOBAL:
                sh.items.append([S('global_label'), name, [S('shape'), S('passive')], [S('at'), p[0], p[1], rot],
                                 [S('fields_autoplaced'), S('yes')], effects(1.27, just),
                                 [S('uuid'), U(sh.name, 'glabel', name, p)],
                                 [S('property'), 'Intersheetrefs', '${INTERSHEET_REFS}', [S('at'), p[0], p[1], 0],
                                  effects(1.27, None, hide=True)]])
            else:
                sh.items.append([S('label'), name, [S('at'), p[0], p[1], rot], effects(1.27, just + ' bottom'),
                                 [S('uuid'), U(sh.name, 'label', name, p)]])
    return used


def paper(sh):
    return [S('paper'), 'User', sh.size[0], sh.size[1]] if sh.size else [S('paper'), sh.paper]


def write_all(proj_dir, title, rev, date, comments, sheets, offset=(4, 4)):
    OX, OY = offset[0] * G, offset[1] * G

    def shift(e):
        if isinstance(e, list) and e:
            if e[0] in ('at', 'xy', 'start', 'end') and len(e) >= 3 and isinstance(e[1], (int, float)):
                e[1] = round(e[1] + OX, 4)
                e[2] = round(e[2] + OY, 4)
            else:
                for x in e[1:]:
                    shift(x)

    emit_labels(sheets)
    tb = [S('title_block'), [S('title'), title], [S('date'), date], [S('rev'), rev], [S('company'), '']]
    for i, c in enumerate(comments):
        tb.append([S('comment'), i + 1, c])
    for sh in sheets:
        for e in sh.items + sh.symbols:
            shift(e)
        used_libs = sorted({find(s, 'lib_id')[1] for s in sh.symbols})
        doc = [S('kicad_sch'), [S('version'), 20250114], [S('generator'), 'eeschema'],
               [S('generator_version'), '10.0'], [S('uuid'), sh.uuid], paper(sh), tb,
               [S('lib_symbols')] + [lib_cache[k] for k in used_libs]] + sh.items + sh.symbols + \
              [[S('embedded_fonts'), S('no')]]
        open(os.path.join(proj_dir, sh.fname), 'w').write(dump(doc) + '\n')
    # root sheet: one sheet symbol per child
    items = []
    for i, sh in enumerate(sheets):
        x, y = 20 + (i % 2) * 120, 30 + (i // 2) * 70
        items.append([S('sheet'), [S('at'), x, y], [S('size'), 90, 45], [S('exclude_from_sim'), S('no')],
                      [S('in_bom'), S('yes')], [S('on_board'), S('yes')], [S('dnp'), S('no')],
                      [S('fields_autoplaced'), S('yes')],
                      [S('stroke'), [S('width'), 0.1524], [S('type'), S('solid')]],
                      [S('fill'), [S('color'), 0, 0, 0, 0.0]], [S('uuid'), sh.uuid],
                      [S('property'), 'Sheetname', sh.name, [S('at'), x, y - 0.7, 0],
                       effects(1.27, 'left bottom')],
                      [S('property'), 'Sheetfile', sh.fname, [S('at'), x, y + 45.6, 0],
                       effects(1.27, 'left top')],
                      [S('instances'), [S('project'), PROJECT,
                                        [S('path'), '/' + ROOT[0], [S('page'), str(sh.page)]]]]])
    root = [S('kicad_sch'), [S('version'), 20250114], [S('generator'), 'eeschema'], [S('generator_version'), '10.0'],
            [S('uuid'), ROOT[0]], [S('paper'), 'A4'], tb, [S('lib_symbols')]] + items + [
           [S('sheet_instances'), [S('path'), '/', [S('page'), '1']]], [S('embedded_fonts'), S('no')]]
    open(os.path.join(proj_dir, PROJECT + '.kicad_sch'), 'w').write(dump(root) + '\n')
