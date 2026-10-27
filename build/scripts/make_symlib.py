#!/usr/bin/env python3
"""Generate lib/E0003.kicad_sym (project symbols) and lib/E0003.pretty footprints.

Pin tables from the datasheets: TPS629210 (SLUSEJ8 Table 6-1), BQ29209 (SLUSA75 Pin Functions),
TPS259470L RPW (SLVSFC9C Table 5-1), MAX17205 TDFN-14 (MAX17201-MAX17215 p.23), ABLIC S-8252 SOT-23-6
(Table 6), PSMN2R0-30YLDX LFPAK56 (1-3 S, 4 G, mb/5 D).
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from sexp import Sym as S, dump

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def eff(hide=False, justify=None):
    e = [S('effects'), [S('font'), [S('size'), 1.27, 1.27]]]
    if justify:
        e.append([S('justify'), S(justify)])
    if hide:
        e.append([S('hide'), S('yes')])
    return e

def prop(k, v, x=0, y=0, hide=True, justify=None):
    return [S('property'), k, v, [S('at'), x, y, 0], eff(hide, justify)]

def pin(typ, num, name, x, y, ang, hide=False, length=2.54):
    p = [S('pin'), S(typ), S('line'), [S('at'), x, y, ang], [S('length'), length]]
    if hide:
        p.append([S('hide'), S('yes')])
    p += [[S('name'), name, eff()], [S('number'), num, eff()]]
    return p

def symbol(name, value, fp, ds, desc, kw, body, pins, fpf, ref='U'):
    x1, y1, x2, y2 = body
    return [S('symbol'), name, [S('exclude_from_sim'), S('no')], [S('in_bom'), S('yes')],
            [S('on_board'), S('yes')],
            prop('Reference', ref, x1, y1 + 1.27, False, 'left'),
            prop('Value', value, x1, y1 + 3.81, False, 'left'),
            prop('Footprint', fp), prop('Datasheet', ds), prop('Description', desc),
            prop('ki_keywords', kw), prop('ki_fp_filters', fpf),
            [S('symbol'), name + '_0_1',
             [S('rectangle'), [S('start'), x1, y1], [S('end'), x2, y2],
              [S('stroke'), [S('width'), 0.254], [S('type'), S('default')]],
              [S('fill'), [S('type'), S('background')]]]],
            [S('symbol'), name + '_1_1'] + pins,
            [S('embedded_fonts'), S('no')]]

def side(pins, x, ang, y0, dy=-2.54):
    out = []
    for i, p in enumerate(pins):
        if p is None:
            continue
        typ, num, nm = p[:3]
        out.append(pin(typ, num, nm, x, y0 + i * dy, ang))
    return out

def gnd(nums, x, y, name='GND'):
    out = [pin('power_in', nums[0], name, x, y, 90)]
    for n in nums[1:]:
        out.append(pin('passive', n, name, x, y, 90, hide=True))
    return out

syms = []
# TPS629210 -----------------------------------------------------------
syms.append(symbol('TPS629210', 'TPS629210DRL', 'Package_TO_SOT_SMD:SOT-583-8',
    'https://www.ti.com/lit/ds/symlink/tps629210.pdf',
    '17 V 1 A synchronous step-down converter, Smart-CONFIG (MODE/S-CONF) and VSET, SOT-583-8',
    'buck regulator step-down', (-12.7, 7.62, 12.7, -7.62),
    side([('power_in', '6', 'VIN'), ('input', '7', 'EN'), ('input', '8', 'MODE/S-CONF')], -15.24, 0, 5.08)
    + side([('output', '4', 'SW'), ('input', '3', 'VOS'), ('input', '1', 'FB/VSET'),
            ('open_collector', '2', 'PG')], 15.24, 180, 5.08)
    + gnd(['5'], 0, -10.16), 'SOT?583*'))
# BQ29209 --------------------------------------------------------------
syms.append(symbol('BQ29209', 'BQ29209DRB', 'Package_SON:VSON-8-1EP_3x3mm_P0.65mm_EP1.65x2.4mm',
    'https://www.ti.com/lit/ds/symlink/bq29209.pdf',
    '2-series Li-ion overvoltage protector with automatic cell balancing, OV 4.30 V, VSON-8',
    'battery protection balancing 2S', (-7.62, 7.62, 7.62, -7.62),
    side([('input', '1', 'VC2'), ('input', '2', 'VC1'), ('passive', '3', 'VC1_CB'), ('passive', '4', 'CD')],
         -10.16, 0, 3.81)
    + [pin('power_in', '7', 'VDD', 0, 10.16, 270)]
    + side([('output', '8', 'OUT'), ('input', '6', '~{CB_EN}')], 10.16, 180, 2.54)
    + gnd(['5', '9'], 0, -10.16), 'VSON*3x3mm*P0.65mm*'))
# TPS259470L -----------------------------------------------------------
syms.append(symbol('TPS259470L', 'TPS259470ARPW', 'E0003:TI_RPW0010A_VQFN-HR-10_2x2mm_P0.475mm',
    'https://www.ti.com/lit/ds/symlink/tps25947.pdf',
    'eFuse 2.7-23 V 5.5 A, adjustable OVLO/UVLO, current limit, ITIMER, reverse blocking, VQFN-HR-10 2x2 (TPS259470A auto-retry / L latch-off)',
    'eFuse hot swap current limit', (-10.16, 7.62, 10.16, -10.16),
    side([('power_in', '5', 'IN'), ('input', '1', 'EN/UVLO'), ('input', '2', 'OVLO'), ('passive', '7', 'DVDT')],
         -12.7, 0, 5.08)
    + side([('power_out', '6', 'OUT'), ('open_collector', '4', '~{FLT}'), ('open_collector', '3', 'AUXOFF'),
            ('passive', '9', 'ILM'), ('passive', '10', 'ITIMER')], 12.7, 180, 5.08)
    + gnd(['8'], 0, -12.7), '*RPW0010A*'))
# MAX17205 -------------------------------------------------------------
syms.append(symbol('MAX17205', 'MAX17205G+', 'Package_DFN_QFN:TDFN-14-1EP_3x3mm_P0.4mm_EP1.78x2.35mm',
    'https://www.analog.com/media/en/technical-documentation/data-sheets/MAX17201-MAX17215.pdf',
    'Stand-alone ModelGauge m5 multi-cell fuel gauge, I2C, TDFN-14 3x3',
    'fuel gauge battery ModelGauge', (-10.16, 10.16, 10.16, -17.78),
    side([('power_in', '5', 'VBATT'), ('input', '7', 'CELL1'), ('input', '6', 'CELL2'), ('input', '13', 'CELLX'),
          None, ('input', '2', 'CSP'), ('input', '4', 'CSN')], -12.7, 0, 7.62)
    + side([('bidirectional', '12', 'SDA'), ('input', '11', 'SCL'), ('open_collector', '8', 'ALRT1'), None,
            ('output', '14', 'THRM'), ('input', '9', 'AIN1'), ('input', '10', 'AIN2'), None,
            ('power_out', '1', 'REG3'), ('power_out', '3', 'REG2')], 12.7, 180, 7.62)
    + gnd(['15'], 0, -20.32), 'TDFN*3x3mm*P0.4mm*'))
# S-8252 ---------------------------------------------------------------
syms.append(symbol('S-8252', 'S-8252AAG-M6T1U', 'Package_TO_SOT_SMD:SOT-23-6',
    'https://www.ablic.com/en/doc/datasheet/battery_protection/S8252_E.pdf',
    'Battery protection IC for 2-serial-cell pack, CMOS DO/CO FET drivers, SOT-23-6',
    'battery protection 2S overcharge overdischarge', (-7.62, 5.08, 7.62, -7.62),
    side([('power_in', '5', 'VDD'), ('input', '4', 'VC'), ('power_in', '6', 'VSS')], -10.16, 0, 2.54)
    + side([('output', '1', 'DO'), ('output', '2', 'CO'), ('input', '3', 'VM')], 10.16, 180, 2.54),
    'SOT?23*'))
# Pack FET (box symbol, LFPAK56) --------------------------------------
syms.append(symbol('PSMN2R0-30YLDX', 'PSMN2R0-30YLDX', 'Package_TO_SOT_SMD:LFPAK56',
    'https://assets.nexperia.com/documents/data-sheet/PSMN2R0-30YLD.pdf',
    'N-MOSFET 30 V 2.0 mOhm logic level, LFPAK56 (pins 1-3 source, 4 gate, tab drain)',
    'nmos mosfet LFPAK56', (-5.08, 5.08, 5.08, -5.08),
    [pin('input', '4', 'G', -7.62, 0, 0), pin('passive', '5', 'D', 0, 7.62, 270),
     pin('passive', '1', 'S', 0, -7.62, 90), pin('passive', '2', 'S', 0, -7.62, 90, hide=True),
     pin('passive', '3', 'S', 0, -7.62, 90, hide=True)], 'LFPAK56*', ref='Q'))

lib = [S('kicad_symbol_lib'), [S('version'), 20251024], [S('generator'), 'e0003_make_symlib'],
       [S('generator_version'), '10.0']] + syms
open(os.path.join(PROJ, 'lib', 'E0003.kicad_sym'), 'w').write(dump(lib) + '\n')

# ---------------------------------------------------------------- footprints
def fp_text(kind, txt, x, y, layer, hide=False):
    e = [S('property'), kind, txt, [S('at'), x, y, 0], [S('layer'), layer],
         [S('effects'), [S('font'), [S('size'), 0.8, 0.8], [S('thickness'), 0.12]]]]
    if hide:
        e.insert(4, [S('hide'), S('yes')])
    return e

def line(x1, y1, x2, y2, layer, w=0.12):
    return [S('fp_line'), [S('start'), x1, y1], [S('end'), x2, y2],
            [S('stroke'), [S('width'), w], [S('type'), S('solid')]], [S('layer'), layer]]

def rect(x1, y1, x2, y2, layer, w=0.05):
    return [S('fp_rect'), [S('start'), x1, y1], [S('end'), x2, y2],
            [S('stroke'), [S('width'), w], [S('type'), S('solid')]], [S('fill'), S('no')], [S('layer'), layer]]

def smd(num, x, y, w, h):
    return [S('pad'), num, S('smd'), S('roundrect'), [S('at'), x, y], [S('size'), w, h],
            [S('layers'), 'F.Cu', 'F.Mask', 'F.Paste'], [S('roundrect_rratio'), 0.1]]

def footprint(name, desc, items, attr='smd'):
    return [S('footprint'), name, [S('version'), 20241229], [S('generator'), 'e0003_make_symlib'],
            [S('generator_version'), '10.0'], [S('layer'), 'F.Cu'],
            [S('descr'), desc], [S('tags'), name], [S('attr'), S(attr)]] + items + [[S('embedded_fonts'), S('no')]]

# TI RPW0010A (VQFN-HR-10, 2x2): pads from the SLVSFC9C land pattern example (p.73), measured from the drawing.
it = [fp_text('Reference', 'REF**', 0, -1.9, 'F.SilkS'), fp_text('Value', 'TI_RPW0010A', 0, 1.9, 'F.Fab')]
def corner(num, sx, sy):
    # L-pad: 0.6 x 0.3 arm on the outer column + 0.25-wide leg running to the package edge (inner side)
    return [smd(num, sx * 0.9, sy * 0.697, 0.6, 0.3), smd(num, sx * 0.725, sy * 1.025, 0.25, 0.356)]
it += corner('1', -1, -1) + [smd('2', -0.9, -0.225, 0.6, 0.25), smd('3', -0.9, 0.225, 0.6, 0.25)] + corner('4', -1, 1)
it += [smd('5', -0.25, 0, 0.3, 2.4), smd('6', 0.25, 0, 0.3, 2.4)]
it += corner('7', 1, 1) + [smd('8', 0.9, 0.225, 0.6, 0.25), smd('9', 0.9, -0.225, 0.6, 0.25)] + corner('10', 1, -1)
it += [rect(-1.0, -1.0, 1.0, 1.0, 'F.Fab', 0.1), rect(-1.45, -1.45, 1.45, 1.45, 'F.CrtYd'),
       line(-1.11, -1.35, -0.5, -1.35, 'F.SilkS'), line(0.5, -1.35, 1.11, -1.35, 'F.SilkS'),
       line(0.5, 1.35, 1.11, 1.35, 'F.SilkS'),
       line(-1.11, 1.35, -0.5, 1.35, 'F.SilkS'),
       [S('fp_circle'), [S('center'), -1.35, -1.25], [S('end'), -1.27, -1.25],
        [S('stroke'), [S('width'), 0.16], [S('type'), S('solid')]], [S('fill'), S('yes')], [S('layer'), 'F.SilkS']]]
open(os.path.join(PROJ, 'lib', 'E0003.pretty', 'TI_RPW0010A_VQFN-HR-10_2x2mm_P0.475mm.kicad_mod'), 'w').write(dump(
    footprint('TI_RPW0010A_VQFN-HR-10_2x2mm_P0.475mm',
              'TI RPW0010A VQFN-HR-10 2x2 mm (TPS25947), land pattern per TI example SLVSFC9C p.73', it)) + '\n')

# 2-pin THT pads for the leaded NTC bead (Semitec 103AT-2), 2.54 mm pitch, 0.8 mm holes
def tht(num, x, shape):
    return [S('pad'), num, S('thru_hole'), S(shape), [S('at'), x, 0], [S('size'), 1.4, 1.4], [S('drill'), 0.8],
            [S('layers'), '*.Cu', '*.Mask']]
it = [fp_text('Reference', 'REF**', 1.27, -1.6, 'F.SilkS'), fp_text('Value', 'NTC_THT', 1.27, 1.6, 'F.Fab'),
      tht('1', 0, 'rect'), tht('2', 2.54, 'circle'), rect(-1.0, -1.0, 3.54, 1.0, 'F.CrtYd')]
open(os.path.join(PROJ, 'lib', 'E0003.pretty', 'NTC_Leaded_THT_P2.54mm_Drill0.8mm.kicad_mod'), 'w').write(dump(
    footprint('NTC_Leaded_THT_P2.54mm_Drill0.8mm', 'Leaded NTC bead (Semitec 103AT-2), 2 THT pads 2.54 mm, 0.8 mm drill', it,
              'through_hole')) + '\n')
print('ok')
