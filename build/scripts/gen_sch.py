#!/usr/bin/env python3
"""Generate the E0005 ESP32-S3 5 V controller schematic (root + 4 hierarchical sheets).

Started from the E0003 generator (same style, same reference designators for the parts that stay).
Run:  python3 build/scripts/gen_sch.py   (then build/scripts/render_check.sh)
Spec: docs/SPEC.md v1.0. Notes: docs/schematic_notes.md.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from sch_core import Sheet, write_all, G, C_PWR, C_BAT, C_MCU, C_PORT, C_UI
import sch_core

# MID and SNS_P keep their global names (as E0003).
sch_core.FORCE_GLOBAL.update({'MID', 'SNS_P', 'CHG_PSEL'})

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

R0402 = 'Resistor_SMD:R_0402_1005Metric'
R0603 = 'Resistor_SMD:R_0603_1608Metric'
C0402 = 'Capacitor_SMD:C_0402_1005Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C1210 = 'Capacitor_SMD:C_1210_3225Metric'
LED0603 = 'LED_SMD:LED_0603_1608Metric'
V25 = {'Voltage': '25V'}
V50 = {'Voltage': '50V'}
V16 = {'Voltage': '16V'}

sch_core.POWER_NETS.clear()
sch_core.POWER_NETS.update({'GND', '+3V3', 'V5', 'VBUS', 'BAT+'})

# Reference designators: parts kept from E0003 keep their E0003 reference (same generation order, removed
# parts are skipped with skip()); parts new in E0005 get numbers above E0003's highest (new()).
cnt = {}
NEW = {'R': 128, 'C': 62, 'D': 28, 'Q': 10, 'U': 15, 'L': 1}

def nref(prefix):
    cnt[prefix] = cnt.get(prefix, 0) + 1
    return '%s%d' % (prefix, cnt[prefix])

def skip(prefix, n=1):
    cnt[prefix] = cnt.get(prefix, 0) + n

def new(prefix):
    NEW[prefix] += 1
    return '%s%d' % (prefix, NEW[prefix])

def two(sh, lib, ref, val, x, y, n1, n2, fp, horiz=False, dnp=False, extra=None, L=1):
    if horiz:
        sh.place(lib, ref, val, x, y, 90, fp=fp, dnp=dnp, extra=extra,
                 refpos=(x, y - 1.1, None), valpos=(x, y + 1.2, None))
    else:
        sh.place(lib, ref, val, x, y, 0, fp=fp, dnp=dnp, extra=extra,
                 refpos=(x + 0.7, y - 0.25, 'left'), valpos=(x + 0.7, y + 0.75, 'left'))
    if n1 is not False:
        sh.net(ref, '1', n1, L) if n1 else None
    if n2 is not False:
        sh.net(ref, '2', n2, L) if n2 else None
    return ref

def R(sh, val, x, y, n1, n2, fp=R0402, ref=None, **kw):
    return two(sh, 'Device:R_Small_US', ref or nref('R'), val, x, y, n1, n2, fp, **kw)

def C(sh, val, x, y, n1, n2, fp=C0402, ref=None, **kw):
    return two(sh, 'Device:C_Small', ref or nref('C'), val, x, y, n1, n2, fp, **kw)

def LED(sh, color, x, y, nA, nK, ref=None):
    """Horizontal LED, anode left."""
    ref = ref or nref('D')
    sh.place('Device:LED_Small', ref, color, x, y, 180, fp=LED0603, refpos=(x, y - 1.1, None),
             valpos=(x, y + 1.2, None))
    sh.net(ref, '2', nA)
    sh.net(ref, '1', nK)
    return ref

def schottky(sh, x, y, nA, nK, ref=None, horiz=True):
    ref = ref or nref('D')
    sh.place('Diode:BAT54W', ref, 'BAT54W', x, y, 180 if horiz else 270, fp='Package_TO_SOT_SMD:SOT-323_SC-70',
             refpos=(x, y - 1.6, None) if horiz else (x + 1.2, y, 'left'),
             valpos=(x, y + 1.6, None) if horiz else (x + 1.2, y + 1, 'left'))
    if nA is not False:
        sh.net(ref, '1', nA)
    if nK is not False:
        sh.net(ref, '3', nK)
    sh.net(ref, '2', None)
    return ref

def divider(sh, vt, vb, x, y, ntop, nmid, nbot, side='right', L=2, refs=(None, None)):
    """Vertical divider: top R at y, bottom R at y+5, mid node wired out to a label."""
    rt = R(sh, vt, x, y, ntop, None, ref=refs[0])
    rb = R(sh, vb, x, y + 5, None, nbot, ref=refs[1])
    a, b = sh.pin(rt, '2'), sh.pin(rb, '1')
    sh.wire(a, b)
    m = (x * G, (y + 2.5) * G)
    sh.junction(m)
    q = ((x + (L if side == 'right' else -L)) * G, m[1])
    sh.wire(m, q)
    sh.label(nmid, q, side)
    return rt, rb

def r_led(sh, x, y, n_in, n_k, color, rval='1k', refs=(None, None)):
    """Horizontal R then LED (anode side towards the R), wired directly."""
    r = R(sh, rval, x, y, n_in, None, horiz=True, ref=refs[0])
    d = refs[1] or nref('D')
    sh.place('Device:LED_Small', d, color, x + 4, y, 180, fp=LED0603, refpos=(x + 4, y - 1.1, None),
             valpos=(x + 4, y + 1.2, None))
    sh.wire(sh.pin(r, '2'), sh.pin(d, '2'))
    sh.net(d, '1', n_k)
    return d

def fet(sh, ref, x, y, g, d, s, lib='Transistor_FET:2N7002', val='2N7002', mirror=None):
    sh.place(lib, ref, val, x, y, 0, mirror=mirror, refpos=(x + 1.5, y - 0.5, 'left'),
             valpos=(x + 1.5, y + 0.5, 'left'))
    sh.net(ref, '1', g)
    sh.net(ref, '2', s)
    sh.net(ref, '3', d)

# =====================================================================================
# Sheet 2: USB-C input, U_IN eFuse, BQ25887 charger, TPS56637 battery buck + soft power latch, 3V3
# =====================================================================================
def fet_pd(sh, ref, x, y, gate, rref, drain=None, rval='100k'):
    """2N7002 at (x, y), source to GND, gate wired to a 100k pull-down and a gate label on the left."""
    sh.place('Transistor_FET:2N7002', ref, '2N7002', x, y, 0, refpos=(x + 1.5, y - 0.5, 'left'),
             valpos=(x + 1.5, y + 0.5, 'left'))
    sh.net(ref, '2', 'GND')
    if drain:
        sh.net(ref, '3', drain)
    g = sh.pin(ref, '1')
    j = (g[0] - 2 * G, g[1])
    sh.wire(g, j, (j[0] - 2 * G, j[1]))
    sh.junction(j)
    sh.label(gate, (j[0] - 2 * G, j[1]), 'left')
    R(sh, rval, j[0] / G, j[1] / G + 2, None, 'GND', ref=rref)
    sh.wire(j, sh.pin(rref, '1'))


def sheet_power():
    sh = Sheet('Power: USB-C, U_IN, charger, 5 V buck, 3V3', 'power.kicad_sch', page=2, size=(530, 410))
    # ---- USB-C
    sh.rect(0, 0, 62, 62, C_PWR, 'USB-C J11 (5 V, no PD), VBUS TVS, USB ESD, CC Rd + sense')
    sh.place('Connector:USB_C_Receptacle_USB2.0_16P', 'J11', 'USB4105-GF-A', 12, 22, 0,
             fp='Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
             refpos=(4, 7, 'left'), valpos=(4, 8, 'left'),
             desc='USB 2.0 Type-C receptacle, 16-pin, 5 A / 20 V, west edge')
    sh.nets('J11', {'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS', 'A5': 'CC1', 'B5': 'CC2',
                    'A6': 'USB_DP_C', 'B6': 'USB_DP_C', 'A7': 'USB_DN_C', 'B7': 'USB_DN_C',
                    'A8': None, 'B8': None, 'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND',
                    'SH': 'USB_SHIELD'}, L=2)
    R(sh, '1M', 6, 46, 'USB_SHIELD', 'GND', ref='R1')
    C(sh, '4.7nF', 10, 46, 'USB_SHIELD', 'GND', extra=V50, ref='C1')
    sh.notes(['Shell: 1M || 4.7nF to GND.'], 2, 51.5)
    sh.place('Diode:SMF9V0A', 'D1', 'SMF9.0A', 40, 10, 270, fp='Diode_SMD:D_SOD-123F',
             refpos=(41.5, 9.5, 'left'), valpos=(41.5, 10.5, 'left'))
    sh.net('D1', '1', 'VBUS')
    sh.net('D1', '2', 'GND')
    sh.place('Power_Protection:USBLC6-2SC6', 'U4', 'USBLC6-2SC6', 46, 26, 0, refpos=(49, 21, 'left'),
             valpos=(49, 22, 'left'))
    sh.nets('U4', {'1': 'USB_DP_C', '6': 'USB_DP_C', '3': 'USB_DN_C', '4': 'USB_DN_C', '5': '+3V3', '2': 'GND'}, L=2)
    R(sh, '0R', 44, 35, 'USB_DP_C', 'USB_DP', horiz=True, L=2, ref='R2')
    R(sh, '0R', 44, 39, 'USB_DN_C', 'USB_DN', horiz=True, L=2, ref='R3')
    # CC: Rd 5.1k to GND, 10k + 1 nF to the ESP32 ADC
    R(sh, '5.1k 1%', 22, 49, 'CC1', 'GND', ref=new('R'))
    R(sh, '5.1k 1%', 29, 49, 'CC2', 'GND', ref=new('R'))
    R(sh, '10k', 39, 46, 'CC1', 'CC1_SENSE', horiz=True, L=2, ref=new('R'))
    R(sh, '10k', 39, 50, 'CC2', 'CC2_SENSE', horiz=True, L=2, ref=new('R'))
    C(sh, '1nF', 53, 49, 'CC1_SENSE', 'GND', ref=new('C'))
    C(sh, '1nF', 58, 49, 'CC2_SENSE', 'GND', ref=new('C'))
    sh.notes(['D1 SMF9.0A: 15.4 V clamp < 20 V BQ25887 / TPS25947 abs max. USBLC6 VBUS pin to +3V3.',
              'D+/D- 90 ohm diff., 0R to GPIO20/19. CC: 5.1k Rd each (dead-battery safe);',
              '10k + 1 nF to GPIO6/7 (ADC1): ~0.41 V default, ~0.92 V 1.5 A, ~1.68 V 3.0 A.'], 2, 56, C_PWR)

    # ---- U_IN eFuse
    sh.rect(64, 0, 130, 62, C_PWR, 'USB INPUT eFUSE U_IN TPS259470A: VBUS -> V5, 0.50 / 1.37 / 2.81 A')
    u = new('U')   # U16
    sh.place('E0005:TPS259470L', u, 'TPS259470ARPW', 104, 14, 0, refpos=(98, 6.5, 'left'),
             valpos=(98, 7.5, 'left'))
    sh.nets(u, {'5': 'VBUS', '6': 'V5', '1': 'UIN_EN', '2': 'UIN_OVLO', '7': 'UIN_DVDT',
                '4': 'USBIN_FLT_N', '3': None, '9': 'UIN_ILM', '10': 'UIN_ITIMER', '8': 'GND'}, L=2)
    divider(sh, '1M 1%', '390k 1%', 67, 7, 'VBUS', 'UIN_EN', 'GND', refs=(new('R'), new('R')))
    divider(sh, '1M 1%', '249k 1%', 76, 7, 'VBUS', 'UIN_OVLO', 'GND', refs=(new('R'), new('R')))
    C(sh, '100nF', 87, 8, 'VBUS', 'GND', extra=V50, ref=new('C'))
    C(sh, '1.8nF', 67, 32, 'UIN_DVDT', 'GND', extra=V50, ref=new('C'))
    C(sh, '22nF', 72, 32, 'UIN_ITIMER', 'GND', extra=V50, ref=new('C'))
    R(sh, '6.65k 1%', 78, 32, 'UIN_ILM', 'GND', ref=new('R'))
    # current-limit legs (cumulative): leg A 3.83k (P06), leg B 2.32k (P07), each R wired to its 2N7002 drain
    for rv, gate, x in (('3.83k 1%', 'USB_ILIM_1A5', 93), ('2.32k 1%', 'USB_ILIM_3A0', 113)):
        rl = new('R')
        R(sh, rv, x + 1, 32, 'UIN_ILM', None, ref=rl)
        q = new('Q')
        fet_pd(sh, q, x, 36, gate, new('R'))
        sh.wire(sh.pin(rl, '2'), sh.pin(q, '3'))
    sh.notes(['I_LIM = 3334 / R_ILM: 6.65k -> 0.50 A (reset), || 3.83k -> 1.37 A (P06), || 2.32k -> 2.81 A (P06+P07).',
              'Legs are cumulative: never P07 without P06. 100k gate pull-downs -> 0.50 A at reset.',
              'OVLO 1M/249k: 6.02 V rising. EN/UVLO 1M/390k: 4.28 V rising / 3.88 V falling.',
              'ITIMER 22 nF (~18 ms), dVdt 1.8 nF. FLT -> TCA9535 P15 (low = at its limit / TSD).',
              'Thermal: keep the SPEC 5.6.1 copper (IN/OUT pours >= 80 mm2, 6 vias each, no reliefs).'],
             66, 50, C_PWR)

    # ---- V5 sense + flags
    sh.rect(132, 0, 196, 26, C_PWR, 'V5 SENSE (GPIO4), POWER FLAGS')
    divider(sh, '100k', '100k', 136, 7, 'V5', 'V5_SENSE', 'GND', refs=(new('R'), new('R')))
    C(sh, '100nF', 145, 12, 'V5_SENSE', 'GND', extra=V50, ref=new('C'))
    sh.notes(['V5 / 2 -> GPIO4 (ADC1_CH3), 2.75 V at 5.5 V.', 'V5 and BAT+ are driven by U16 OUT / U2 BAT.'],
             134, 21, C_PWR)
    for net, x in (('VBUS', 162), ('GND', 170)):
        sh.flag(net, x, 7)

    # ---- BQ25887 charger
    sh.rect(0, 64, 100, 116, C_PWR, 'CHARGER BQ25887 (I2C0 0x6A): 5 V USB -> 2S boost, 1.5 MHz, balancing')
    sh.place('Battery_Management:BQ25887RGE', 'U2', 'BQ25887RGET', 46, 92, 0, refpos=(43, 82, 'left'),
             valpos=(43, 83, 'left'))
    sh.nets('U2', {'23': 'VBUS', '2': 'CHG_STAT', '1': 'CHG_PG_N', '5': 'I2C0_SCL', '4': 'I2C0_SDA',
                   '6': 'CHG_INT_N', '24': 'CHG_PSEL', '3': 'CHG_CD', '15': 'CHG_SNS', '16': 'CHG_SNS',
                   '8': 'CHG_ILIM', '19': 'GND', '20': 'GND', '25': 'GND', '21': 'CHG_PMID', '22': 'CHG_PMID',
                   '17': 'CHG_SW', '18': 'CHG_SW', '12': 'CHG_BTST', '13': 'BAT+', '14': 'BAT+', '9': 'CHG_MID',
                   '10': 'CHG_CBSET', '11': 'REGN', '7': 'CHG_TS'}, L=2)
    C(sh, '1uF', 4, 72, 'VBUS', 'GND', fp=C0603, extra=V50, ref='C2')
    C(sh, '10uF', 9, 72, 'CHG_PMID', 'GND', fp=C0805, extra=V25, ref='C8')
    C(sh, '10uF', 14, 72, 'CHG_PMID', 'GND', fp=C0805, extra=V25, ref='C9')
    sh.place('Device:L', 'L2', '1uH', 25, 71, 90, fp='Inductor_SMD:L_Vishay_IHLP-2525',
             refpos=(25, 69.5, None), valpos=(25, 72.6, None),
             desc='1 uH, 11 A rated / 22 A Isat, 10 mOhm (charger boost, PMID -> SW)')
    sh.net('L2', '1', 'CHG_PMID', 2)
    sh.net('L2', '2', 'CHG_SW', 2)
    C(sh, '47nF', 37, 72, 'CHG_BTST', 'CHG_SW', extra=V50, ref='C11')
    R(sh, '10k', 4, 86, '+3V3', 'CHG_CD', ref='R12')
    R(sh, '10k', 9, 86, '+3V3', 'CHG_PSEL', ref=new('R'))
    R(sh, '374R 1%', 14, 86, 'CHG_ILIM', 'GND', ref=new('R'))
    r_led(sh, 20, 98, '+3V3', 'CHG_STAT', 'amber', refs=('R13', 'D2'))
    for i in range(2):
        C(sh, '47uF', 60 + 5 * i, 72, 'CHG_SNS', 'GND', fp=C1210, extra=V16, ref=new('C'))
    C(sh, '10uF', 70, 72, 'BAT+', 'GND', fp=C0805, extra=V25, ref='C18')
    C(sh, '4.7uF', 75, 72, 'REGN', 'GND', fp=C0603, extra=V25, ref='C20')
    divider(sh, '5.23k 1%', '30.1k 1%', 62, 86, 'REGN', 'CHG_TS', 'GND', refs=('R10', 'R11'))
    R(sh, '300R', 78, 90, 'CHG_MID', 'MID', horiz=True, L=2, ref=new('R'))
    R(sh, '39R 1% 1W', 78, 95, 'CHG_CBSET', 'MID', fp='Resistor_SMD:R_2512_6332Metric', horiz=True, L=2,
      ref=new('R'))
    sh.notes(['Per BQ25887 Fig. 69: VBUS 1 uF, PMID 2 x 10 uF/25 V, L 1 uH PMID -> SW, BTST 47 nF, SNS 2 x 47 uF/16 V,',
              'BAT 10 uF, REGN 4.7 uF. TS: REGN 5.23k / 30.1k || NTC1 103AT-2 (battery sheet) -> JEITA 0-60 C.',
              'ILIM 374R -> 2.97 A hardware cap (K_ILIM 1110). PSEL 10k up -> 500 mA default input limit.',
              'CD 10k up -> HIZ / charging OFF at reset (TCA9535 P05 drives low). PG -> P16, INT -> GPIO5.',
              'MID 300R (bottom-cell reverse protection), CBSET 39R 2512 -> ~108 mA balancing (0.45 W).',
              'BAT = BAT+ after F1. SNS is the boost output (internal R_SNS to BAT): caps only.'],
             2, 107, C_PWR)

    # ---- TPS56637 battery buck + soft power latch
    sh.rect(102, 64, 196, 116, C_PWR, 'BATTERY -> V5 BUCK TPS56637 (4.80 V, Eco-mode) + SOFT POWER LATCH')
    # latch: Q_PL P-FET BAT+ -> EN divider, 39k gate-source, 10k to PL_PULL (button via D13 or the hold FET)
    X, Y = 120, 76
    qpl = new('Q')
    sh.place('Transistor_FET:AO3401A', qpl, 'AO3401A', X, Y, 0, mirror='x', refpos=(X + 1.5, Y - 0.5, 'left'),
             valpos=(X + 1.5, Y + 0.5, 'left'))
    sh.net(qpl, '2', 'BAT+')
    rg, rs = new('R'), new('R')
    R(sh, '39k', X - 4, Y - 2, 'BAT+', None, ref=rg)
    R(sh, '10k', X - 4, Y + 2, None, None, ref=rs)
    gate = sh.pin(qpl, '1')
    jg = (gate[0] - 2 * G, gate[1])
    sh.wire(sh.pin(rg, '2'), jg, sh.pin(rs, '1'))
    sh.wire(jg, gate)
    sh.junction(jg)
    qh = new('Q')
    fet_pd(sh, qh, X - 5, Y + 10, 'PWR_HOLD', new('R'))
    jp = (jg[0], jg[1] + 5 * G)
    sh.wire(sh.pin(rs, '2'), jp, sh.pin(qh, '3'))
    sh.junction(jp)
    sh.wire(jp, (jp[0] - 2 * G, jp[1]))
    sh.label('PL_PULL', (jp[0] - 2 * G, jp[1]), 'left')
    ren = divider(sh, '200k 1%', '53.6k 1%', X + 1, Y + 5, None, 'BUCK_EN', 'GND', refs=(new('R'), new('R')))
    sh.wire(sh.pin(qpl, '3'), sh.pin(ren[0], '1'))
    ub = new('U')   # U17
    sh.place('E0005:TPS56637', ub, 'TPS56637RPAR', 152, 84, 0, refpos=(145, 76, 'left'), valpos=(145, 77, 'left'))
    sh.nets(ub, {'8': 'BAT+', '1': 'BUCK_EN', '6': 'BUCK_SW', '7': 'BUCK_BOOT', '2': 'BUCK_FB', '4': 'BUCK_PG',
                 '9': 'GND', '3': 'GND', '5': None}, L=2)
    sh.net(ub, '10', 'GND', 1)
    for i, (v, fp_, ex) in enumerate((('10uF', C0805, V25), ('10uF', C0805, V25), ('100nF', C0402, V50))):
        C(sh, v, 134 + 4 * i, 70, 'BAT+', 'GND', fp=fp_, extra=ex, ref=new('C'))
    C(sh, '100nF', 160, 70, 'BUCK_BOOT', 'BUCK_SW', extra=V50, ref=new('C'))
    sh.place('Device:L', 'L1', '2.2uH', 170, 69, 90, fp='Inductor_SMD:L_Bourns_SRP7028A_7.3x6.6mm',
             refpos=(170, 67.5, None), valpos=(170, 70.6, None),
             desc='2.2 uH, 8 A rated / 14 A Isat, 20 mOhm, shielded (5 V buck)')
    sh.net('L1', '1', 'BUCK_SW', 2)
    sh.net('L1', '2', 'V5', 2)
    for i in range(4):
        C(sh, '47uF', 178 + 4 * i, 70, 'V5', 'GND', fp=C1210, extra=V16, ref=new('C'))
    divider(sh, '69.8k 1%', '10k 1%', 176, 82, 'V5', 'BUCK_FB', 'GND', side='left', refs=(new('R'), new('R')))
    rff, cff = new('R'), new('C')
    R(sh, '20k', 183, 86, 'V5', None, horiz=True, ref=rff)
    C(sh, '100pF', 188, 86, None, 'BUCK_FB', horiz=True, ref=cff, L=2)
    sh.wire(sh.pin(rff, '2'), sh.pin(cff, '1'))
    sh.notes(['FB 69.8k/10k: 0.6 x (1 + 6.98) = 4.79 V. FF 20k + 100 pF (Table 4, 5 V row). MODE = GND -> Eco-mode',
              '(no reverse current: V5 diode-OR with U_IN). L1 2.2 uH, 4 x 47 uF here + 2 at the ports (SPEC 5.1.1).',
              'EN 200k / 53.6k from Q_PL: 5.38 V rising (5.76 V max), 4.30 V falling (Ip 1 uA, Ih 4 uA); 1.99 V at 8.4 V.',
              'Latch: Q_PL AO3401A (-30 V, +-12 V), 39k gate-source -> VGS -6.7 V at 8.4 V. Press: PB_RAW low -> D13',
              '(MCU sheet) pulls PL_PULL -> Q_PL on -> buck on -> firmware sets PWR_HOLD (GPIO36). Off: PWR_HOLD low.',
              'USB + battery: keep PWR_HOLD high (EN low turns on the 200R SW discharge, ~25 mA from V5).',
              'PG -> TCA9535 P17 (10k up on ports sheet).'], 104, 104, C_PWR)

    # ---- 3V3 buck
    sh.rect(0, 118, 100, 150, C_PWR, '3V3 BUCK TPS629210 (from V5, 1 A)')
    sh.place('E0005:TPS629210', 'U5', 'TPS629210DRL', 36, 134, 0, refpos=(26, 128, 'left'),
             valpos=(26, 129, 'left'))
    sh.tie('U5', ['6', '7'], 'V5')
    sh.nets('U5', {'8': 'BUCK_MODE', '1': None, '2': None, '4': 'BUCK_SW_3V3', '5': 'GND'}, L=2)
    vos = sh.pin('U5', '3')
    corner = (vos[0] + 3 * G, vos[1])
    sh.wire(vos, corner, (corner[0], corner[1] + 2 * G))
    sh.power('+3V3', (corner[0], corner[1] + 2 * G), flip=True)
    C(sh, '10uF', 6, 134, 'V5', 'GND', fp=C0805, extra=V25, ref='C22')
    C(sh, '100nF', 10, 134, 'V5', 'GND', extra=V50, ref='C23')
    R(sh, '27.4k 1%', 16, 139, 'BUCK_MODE', 'GND', ref='R14')
    sh.place('Device:L', 'L3', '2.2uH', 64, 132, 90, fp='Inductor_SMD:L_1008_2520Metric',
             refpos=(64, 130.5, None), valpos=(64, 133.6, None))
    sh.net('L3', '1', 'BUCK_SW_3V3', 2)
    sh.net('L3', '2', '+3V3', 2)
    C(sh, '22uF', 74, 134, '+3V3', 'GND', fp=C0805, extra={'Voltage': '6.3V'}, ref='C24')
    sh.flag('+3V3', 82, 131)
    sh.notes(['MODE/S-CONF 27.4k: VSET mode, auto PFM/PWM, output discharge. FB/VSET open -> 3.3 V.',
              'EN tied to V5; 100 % duty down to ~3.5 V V5. PG unused.'], 2, 146, C_PWR)
    cnt.update({'R': 14, 'C': 24, 'D': 2})   # E0003 counter state after its power sheet
    return sh

# =====================================================================================
# Sheet 3: battery pack, protection, gauge
# =====================================================================================
def sheet_battery():
    sh = Sheet('Battery pack, protection, gauge', 'battery.kicad_sch', page=3, size=(500, 340))
    sh.rect(0, 0, 70, 70, C_BAT, 'CELLS (bottom side), F1, REVERSE-CELL LEDS, NTCs')
    MECH = 'E0005_mech:Keystone_1121_1x21700_THM'
    for ref, x, y, p, n, txt in (('BH2', 14, 16, 'CELL2_P', 'MID', 'Cell 2 (top)'),
                                 ('BH1', 14, 40, 'MID', 'B_N', 'Cell 1 (bottom)')):
        sh.place('Device:Battery_Cell', ref, 'Keystone 1121 + P50B', x, y, 0, fp=MECH,
                 refpos=(x + 2, y - 1, 'left'), valpos=(x + 2, y, 'left'),
                 desc='21700 holder Keystone 1121 (bottom side), Molicel P50B cell; pad 1 = +, pad 2 = -')
        sh.net(ref, '1', p, 2)
        sh.net(ref, '2', n, 2)
        sh.text(txt, x + 2, y + 1.2)
    sh.place('Device:Fuse', 'F1', '10A T', 30, 8, 90, fp='Fuse:Fuse_Littelfuse-NANO2-451_453',
             refpos=(30, 6.5, None), valpos=(30, 9.7, None), desc='10 A time-lag SMD fuse, 125 V (pack fuse)')
    sh.net('F1', '1', 'CELL2_P', 2)
    sh.net('F1', '2', 'BAT+', 2)
    for k, cp, cn, x, y in ((2, 'CELL2_P', 'MID', 38, 20), (1, 'MID', 'B_N', 38, 44)):
        r = R(sh, '2.2k', x, y, cn, None, horiz=True)
        d = schottky(sh, x + 6, y, False, False)
        sh.wire(sh.pin(r, '2'), sh.pin(d, '1'))
        led = nref('D')
        sh.place('Device:LED_Small', led, 'red', x + 13, y, 180, fp=LED0603, refpos=(x + 13, y - 1.1, None),
                 valpos=(x + 13, y + 1.2, None))
        sh.wire(sh.pin(d, '3'), sh.pin(led, '2'))
        sh.net(led, '1', cp)
    sh.notes(['Reverse-cell LED: R + BAT54W + red LED, oriented to light only when that cell is reversed.'], 30, 50)
    sh.place('Device:Thermistor_NTC', 'RT1', '10k B3435', 8, 60, 0,
             fp='E0005:NTC_Leaded_THT_P2.54mm_Drill0.8mm', refpos=(9.5, 59, 'left'), valpos=(9.5, 60, 'left'),
             desc='NTC 10k B3435 Semitec 103AT-2 leaded bead, bonded to the cans (charger TS)')
    sh.net('RT1', '1', 'CHG_TS')
    sh.net('RT1', '2', 'GND')
    sh.place('Device:Thermistor_NTC', 'RT2', '10k B3435', 22, 60, 0,
             fp='E0005:NTC_Leaded_THT_P2.54mm_Drill0.8mm', refpos=(23.5, 59, 'left'), valpos=(23.5, 60, 'left'),
             desc='NTC 10k B3435 Semitec 103AT-2 leaded bead, bonded to the cans (gauge AIN1)')
    sh.net('RT2', '1', 'GAUGE_AIN1')
    sh.net('RT2', '2', 'GND')
    sh.notes(['RT1 (NTC1) -> BQ25887 TS, RT2 (NTC2) -> gauge AIN1; both between the cells.'], 2, 67)

    # ---- protection
    sh.rect(72, 0, 186, 70, C_BAT, 'PROTECTION S-8252AAG + LOW-SIDE FETS, R_SENSE')
    sh.place('E0005:S-8252', 'U6', 'S-8252AAG-M6T1U', 100, 30, 0, refpos=(93, 24, 'left'), valpos=(93, 25, 'left'))
    sh.nets('U6', {'5': 'S8252_VDD', '4': 'S8252_VC', '6': 'B_N', '1': 'DSG_G', '2': 'CHG_G', '3': 'S8252_VM'}, L=2)
    R(sh, '470R', 80, 12, 'CELL2_P', 'S8252_VDD')
    R(sh, '470R', 85, 12, 'MID', 'S8252_VC')
    C(sh, '100nF', 80, 26, 'S8252_VDD', 'S8252_VC', extra=V50)
    C(sh, '100nF', 85, 26, 'S8252_VC', 'B_N', extra=V50)
    schottky(sh, 80, 46, 'S8252_VC', 'S8252_VDD', horiz=False)
    schottky(sh, 85, 46, 'B_N', 'S8252_VC', horiz=False)
    R(sh, '2k', 120, 22, 'S8252_VM', 'GND')
    sh.place('E0005:PSMN2R0-30YLDX', 'Q1', 'PSMN2R0-30YLDX', 132, 40, 0, refpos=(134, 36, 'left'),
             valpos=(134, 37, 'left'), desc='Discharge FET (cell side), 30 V 2 mOhm LFPAK56')
    sh.place('E0005:PSMN2R0-30YLDX', 'Q2', 'PSMN2R0-30YLDX', 150, 40, 0, refpos=(152, 36, 'left'),
             valpos=(152, 37, 'left'), desc='Charge FET (pack side), 30 V 2 mOhm LFPAK56')
    sh.net('Q1', '4', 'DSG_G', 2)
    sh.net('Q2', '4', 'CHG_G', 2)
    sh.net('Q1', '1', 'B_N', 2)
    sh.net('Q2', '1', 'SNS_P', 2)
    sh.net('Q1', '5', 'FET_D', 2)
    sh.net('Q2', '5', 'FET_D', 2)
    R(sh, '5mR 1%', 170, 40, 'SNS_P', 'GND', fp='Resistor_SMD:R_2512_6332Metric',
      extra={'Note': 'Kelvin: CSP/CSN taps at the pads'})
    sh.notes(['Pack path: Cell1(-) = B_N -> Q1 (DSG, S at B_N) -> FET_D -> Q2 (CHG) -> SNS_P -> R_SENSE 5 mOhm -> GND.',
              'S-8252AAG: OV 4.30 V, UV 2.80 V, OC 0.150 V (VM after R_SENSE -> ~17-21 A, short guard); F1 = OC limit.',
              'R 470R + C 100nF per ABLIC Table 11; 2k on VM. BAT54W clamps: reverse-cell protection of VC.',
              'Cell OV ladder: VREG 4.20 V -> S-8252 4.30 V -> BQ25887 cell OVP ~4.37 V. No BQ29209 (owner Q2).'],
             74, 59, C_BAT)
    # E0003 BQ29209 balancer / OV2 block removed (owner Q2): its references stay unused
    skip('R', 3); skip('C', 3); skip('R', 1); skip('C', 1); skip('D', 2); skip('R', 3)

    # ---- gauge (E0003 layout shifted 94 grid left)
    dx = -94
    sh.rect(94 + dx, 72, 186 + dx, 124, C_BAT, 'FUEL GAUGE MAX17205 (stack-only, board GND)')
    sh.place('E0005:MAX17205', 'U15', 'MAX17205G+', 132 + dx, 98, 0, refpos=(125 + dx, 85, 'left'),
             valpos=(125 + dx, 86, 'left'))
    sh.tie('U15', ['7', '6', '13'], 'GND')
    sh.nets('U15', {'5': 'GAUGE_VBATT', '7': 'GND', '6': 'GND', '13': 'GND', '2': 'SNS_P', '4': 'GAUGE_CSN',
                    '12': 'GAUGE_SDA', '11': 'GAUGE_SCL', '8': 'GAUGE_ALRT', '14': 'GAUGE_THRM',
                    '9': 'GAUGE_AIN1', '10': 'GND', '1': 'GAUGE_REG3', '3': 'GAUGE_REG2', '15': 'GND'}, L=2)
    R(sh, '49.9R', 100 + dx, 78, 'BAT+', 'GAUGE_VBATT')
    C(sh, '100nF', 105 + dx, 84, 'GAUGE_VBATT', 'GND', extra=V50)
    sh.place('Device:NetTie_2', 'NT1', 'NetTie_2', 108 + dx, 112, 0, fp='NetTie:NetTie-2_SMD_Pad0.5mm',
             refpos=(108 + dx, 110.5, None), valpos=(108 + dx, 113.5, None), in_bom=False, hide_value=True,
             desc='Kelvin tap: gauge CSN to the GND pad of R_SENSE')
    sh.net('NT1', '1', 'GAUGE_CSN')
    sh.net('NT1', '2', 'GND')
    R(sh, '150R', 160 + dx, 80, 'GAUGE_SDA', 'I2C0_SDA', horiz=True, L=2)
    R(sh, '150R', 160 + dx, 84, 'GAUGE_SCL', 'I2C0_SCL', horiz=True, L=2)
    R(sh, '1k', 160 + dx, 88, 'GAUGE_ALRT', 'GAUGE_ALRT_N', horiz=True, L=2)
    R(sh, '10k 1%', 160 + dx, 96, 'GAUGE_THRM', 'GAUGE_AIN1')
    C(sh, '0.47uF', 166 + dx, 104, 'GAUGE_REG3', 'GND')
    C(sh, '0.47uF', 171 + dx, 104, 'GAUGE_REG2', 'GND')
    skip('R', 2); skip('C', 1)   # E0003 MID -> GPIO4 divider removed
    sh.notes(['Per MAX17205 Fig. 2 (low-side protector): GND/EP = board GND, CELL1/2/X = GND, PackCfg BtEn=1, CxEn=0, ChEn=0.',
              'CSP = SNS_P (FET side of R_SENSE), CSN via NT1 Kelvin tap. VBATT 49.9R + 100 nF from BAT+.',
              'THRM -> 10k -> AIN1 + RT2. AIN2 unused (GND). I2C0 0x36/0x0B, 150R series; ALRT 1k -> GPIO35.'],
             96 + dx, 117, C_BAT)
    for net, x in (('B_N', 46), ('S8252_VDD', 52), ('GAUGE_VBATT', 58)):
        sh.flag(net, x, 2)
    return sh

# =====================================================================================
# Sheet 4: MCU, buttons, LEDs, LCD, switch inputs
# =====================================================================================
def sheet_mcu():
    sh = Sheet('MCU, UI, LCD, switches', 'mcu.kicad_sch', page=4, size=(520, 380))
    sh.rect(0, 0, 96, 124, C_MCU, 'ESP32-S3-WROOM-1-N16R2')
    sh.place('RF_Module:ESP32-S3-WROOM-1', 'U1', 'ESP32-S3-WROOM-1-N16R2', 46, 56, 0, refpos=(36, 26, 'left'),
             valpos=(36, 27, 'left'))
    sh.nets('U1', {'1': 'GND', '40': 'GND', '41': 'GND', '2': '+3V3', '3': 'EN', '27': 'BOOT',
                   '39': 'I2C1_SDA', '38': 'I2C1_SCL', '15': None, '4': 'V5_SENSE', '5': 'CHG_INT_N',
                   '6': 'CC1_SENSE', '7': 'CC2_SENSE', '12': 'I2C0_SDA', '17': 'I2C0_SCL', '18': 'LCD_CS',
                   '19': 'LCD_MOSI_MCU', '20': 'LCD_SCK_MCU', '21': 'LCD_MISO', '22': 'LCD_DC', '8': 'SW1',
                   '9': 'SW2', '10': 'SW3', '11': 'SW4', '13': 'USB_DN', '14': 'USB_DP', '23': 'PWR_BTN_N',
                   '28': 'GAUGE_ALRT_N', '29': 'PWR_HOLD', '30': 'SPARE37', '31': 'MUX_RST_N', '32': 'LCD_RST',
                   '33': 'LED_STATUS', '34': 'LCD_SDCS', '35': 'TOUCH_INT_N', '37': None, '36': None,
                   '26': None, '16': None, '24': 'LCD_LITE', '25': 'EXP_INT_N'}, L=2)
    C(sh, '22uF', 6, 8, '+3V3', 'GND', fp=C0805, extra={'Voltage': '6.3V'})
    C(sh, '100nF', 10, 8, '+3V3', 'GND', extra=V50)
    # pull-ups (E0003 order; the PD_ALERT_N one is gone)
    i = 0
    for nn in ('EN', 'BOOT', 'GAUGE_ALRT_N', 'CHG_INT_N', None, 'EXP_INT_N', 'MUX_RST_N', 'TOUCH_INT_N', 'PWR_BTN_N'):
        if nn is None:
            skip('R')
            continue
        R(sh, '10k', 72 + 3 * i if i < 7 else 72, 8 if i < 7 else 20, '+3V3', nn)
        i += 1
    R(sh, '2.2k', 72, 32, '+3V3', 'I2C0_SDA')
    R(sh, '2.2k', 76, 32, '+3V3', 'I2C0_SCL')
    C(sh, '1uF', 14, 8, 'EN', 'GND')
    sh.notes(['EN 10k / 1 uF RC. Strapping: GPIO0 BOOT 10k up; GPIO3, 45, 46 NC. No test points (owner rule).',
              'N16R2: quad PSRAM, GPIO35-37 usable (35 gauge ALRT, 36 PWR_HOLD, 37 spare).',
              'ADC1: GPIO4 V5_SENSE, GPIO6/7 CC1/CC2_SENSE (power sheet). GPIO48 = TCA9535 INT.',
              'I2C0 (system) 2.2k pull-ups here. Interrupt lines 10k pull-ups.'], 2, 119, C_MCU)
    sh.place('Switch:SW_Push', 'SW2', 'BOOT', 88, 46, 270, fp='Button_Switch_SMD:SW_SPST_PTS810',
             refpos=(90, 45, 'left'), valpos=(90, 47, 'left'))
    sh.net('SW2', '1', 'BOOT')
    sh.net('SW2', '2', 'GND')
    sh.place('Switch:SW_Push', 'SW3', 'RESET', 88, 58, 270, fp='Button_Switch_SMD:SW_SPST_PTS810',
             refpos=(90, 57, 'left'), valpos=(90, 59, 'left'))
    sh.net('SW3', '1', 'EN')
    sh.net('SW3', '2', 'GND')
    r_led(sh, 80, 72, 'LED_STATUS', 'GND', 'green')

    # ---- power button
    sh.rect(98, 0, 186, 38, C_UI, 'POWER BUTTON SW1 + J12 (soft power latch on, GPIO21 sense)')
    sh.place('Switch:SW_Push', 'SW1', 'PWR', 106, 18, 270, fp='Button_Switch_SMD:SW_SPST_PTS810',
             refpos=(108, 17, 'left'), valpos=(108, 19, 'left'))
    sh.net('SW1', '1', 'PB_RAW')
    sh.net('SW1', '2', 'GND')
    sh.place('Connector_Generic_MountingPin:Conn_01x02_MountingPin', 'J12', 'SM02B-GHS-TB', 120, 18, 0,
             fp='Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal', refpos=(120, 14, None),
             valpos=(120, 23, None), desc='Panel power button, JST-GH 2-pin')
    sh.nets('J12', {'1': 'PB_RAW', '2': 'GND', 'MP': 'GND'}, L=2)
    de = nref('D')
    sh.place('Device:D_TVS', de, 'TPD1E10B09', 130, 18, 270, fp='Diode_SMD:D_0402_1005Metric',
             refpos=(131.5, 17.5, 'left'), valpos=(131.5, 18.5, 'left'),
             desc='ESD 9 V bidirectional, low leakage (PB_RAW idles at up to BAT+ 8.4 V)')
    sh.net(de, '1', 'PB_RAW')
    sh.net(de, '2', 'GND')
    schottky(sh, 150, 12, 'PL_PULL', 'PB_RAW')
    schottky(sh, 150, 24, 'PWR_BTN_N', 'PB_RAW')
    sh.notes(['Press: PB_RAW low -> PL_PULL low (latch on, power sheet) + GPIO21 low (wake). Long press: firmware',
              'drops PWR_HOLD. PB_RAW floats up to BAT+ when idle: 9 V ESD (not PESD5V0), GPIO21 diode blocks it.'],
             100, 33, C_UI)

    # ---- switch inputs J6-J9
    sh.rect(98, 40, 186, 80, C_UI, 'SWITCH INPUTS J6-J9 (JST-GH 2p: 1 = SWn, 2 = GND)')
    for i in range(4):
        x = 104 + 21 * i
        j = 'J%d' % (6 + i)
        sh.place('Connector_Generic_MountingPin:Conn_01x02_MountingPin', j, 'SM02B-GHS-TB', x, 50, 0, mirror='y',
                 fp='Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal', refpos=(x, 46, None),
                 valpos=(x, 47, None), desc='Switch input SW%d, JST-GH 2-pin' % (i + 1))
        sh.nets(j, {'1': 'SW%d_IN' % (i + 1), '2': 'GND', 'MP': 'GND'})
        R(sh, '4.7k', x + 10, 47, '+3V3', 'SW%d_IN' % (i + 1))
        dref = nref('D')
        sh.place('Diode:PESD5V0L1UL', dref, 'PESD5V0L1UL', x + 4, 58, 270, refpos=(x + 5.5, 57.5, 'left'),
                 valpos=(x + 5.5, 58.5, 'left'))
        sh.net(dref, '1', 'SW%d_IN' % (i + 1))
        sh.net(dref, '2', 'GND')
        R(sh, '1k', x + 4, 68, 'SW%d_IN' % (i + 1), 'SW%d' % (i + 1), horiz=True)
        C(sh, '100nF', x + 10, 72, 'SW%d' % (i + 1), 'GND', extra=V50)
    sh.notes(['4.7k pull-up at the connector, ESD, 1k series, 100 nF at the GPIO (GPIO15-18, RTC wake).'],
             100, 78, C_UI)

    # ---- LCD
    sh.rect(98, 82, 186, 124, C_UI, 'LCD J10: EYESPI 18p 0.5 mm FPC (Adafruit 4311 / 2.8" EYESPI)')
    sh.place('Connector_Generic_MountingPin:Conn_01x18_MountingPin', 'J10', 'FH12-18S-0.5SH', 112, 97, 0,
             mirror='y', fp='Connector_FFC-FPC:Hirose_FH12-18S-0.5SH_1x18-1MP_P0.50mm_Horizontal',
             refpos=(112, 85.5, None), valpos=(112, 86.5, None),
             desc='EYESPI 18-pin 0.5 mm FPC, bottom contact, pin order per Adafruit EYESPI breakout')
    sh.nets('J10', {'1': '+3V3', '2': 'LCD_LITE', '3': 'GND', '4': 'LCD_SCK', '5': 'LCD_MOSI', '6': 'LCD_MISO',
                    '7': 'LCD_DC', '8': 'LCD_RST', '9': 'LCD_CS', '10': 'LCD_SDCS', '11': 'LCD_MEMCS',
                    '12': 'LCD_TSCS', '13': 'LCD_SCL', '14': 'LCD_SDA', '15': 'TOUCH_INT_N', '16': None,
                    '17': 'EYESPI_GP1', '18': None, 'MP': 'GND'}, L=2)
    R(sh, '33R', 130, 88, 'LCD_SCK_MCU', 'LCD_SCK', horiz=True, L=2)
    R(sh, '33R', 130, 92, 'LCD_MOSI_MCU', 'LCD_MOSI', horiz=True, L=2)
    R(sh, '10k', 146, 92, '+3V3', 'LCD_MEMCS')
    R(sh, '10k', 150, 92, '+3V3', 'LCD_TSCS')
    R(sh, '10k', 154, 92, '+3V3', 'LCD_SDCS')
    R(sh, '0R', 130, 100, 'SPARE37', 'EYESPI_GP1', horiz=True, L=2, dnp=True)
    skip('R')   # E0003 GP2 option (GPIO37) dropped: GPIO36 is PWR_HOLD
    C(sh, '10uF', 160, 92, '+3V3', 'GND', fp=C0805, extra=V25)
    C(sh, '100nF', 164, 92, '+3V3', 'GND', extra=V50)
    sh.notes(['Pin order from Adafruit EYESPI breakout (EYE_SPI_DISPLAY_BOTCONTACT): 1 VIN 2 LITE 3 GND 4 SCK',
              '5 MOSI 6 MISO 7 DC 8 RST 9 TCS 10 SDCS 11 MEMCS 12 TSCS 13 SCL 14 SDA 15 INT 16 BUSY 17 GP1 18 GP2.',
              'SCL/SDA = mux ch5 (4.7k on ports sheet). Unused selects 10k up. GP1 via DNP 0R from GPIO37; GP2 NC.'],
             100, 115, C_UI)
    return sh

# =====================================================================================
# Sheet 5: I2C mux, I/O expander, 5 port eFuses + connectors
# =====================================================================================
def sheet_ports():
    sh = Sheet('I2C mux, expander, 5 V peripheral ports', 'ports.kicad_sch', page=5, size=(720, 460))
    sh.rect(0, 0, 112, 70, C_PORT, 'I2C1 MUX PCA9548APW (0x70)')
    sh.place('Interface_Expansion:PCA9548APW', 'U8', 'PCA9548APW', 30, 34, 0, refpos=(22, 14, 'left'),
             valpos=(22, 15, 'left'))
    sh.tie('U8', ['21', '2', '1'], 'GND')
    m = {'1': 'GND', '2': 'GND', '21': 'GND', '12': 'GND', '24': '+3V3', '3': 'MUX_RST_N', '22': 'I2C1_SCL',
         '23': 'I2C1_SDA'}
    chans = ['PORT1', 'PORT2', 'PORT3', 'PORT4', 'PORT5', 'LCD', 'MUX6', 'MUX7']
    for c in range(8):
        m[str(4 + 2 * c if c < 4 else 13 + 2 * (c - 4))] = chans[c] + '_SDA'
        m[str(5 + 2 * c if c < 4 else 14 + 2 * (c - 4))] = chans[c] + '_SCL'
    sh.nets('U8', m, L=2)
    C(sh, '100nF', 8, 8, '+3V3', 'GND', extra=V50)
    R(sh, '10k', 12, 8, '+3V3', 'I2C1_SDA')
    R(sh, '10k', 16, 8, '+3V3', 'I2C1_SCL')
    for c, ch in enumerate(chans):
        val = '4.7k' if c < 6 else '10k'
        R(sh, val, 50 + 7 * c, 12, '+3V3', ch + '_SDA')
        R(sh, val, 53 + 7 * c, 20, '+3V3', ch + '_SCL')
    sh.notes(['A0-A2 = GND -> 0x70. RESET <- GPIO38 (10k up on MCU sheet). Upstream 10k pull-ups.',
              'ch0-ch3 -> J1-J4 (E0001 5 V rev.), ch4 -> J5 (E0002 5 V rev.), ch5 -> EYESPI touch: 4.7k to 3V3.',
              'ch6/ch7 spare: 10k pull-ups. Firmware: <= 4 channels open, writes only.'], 2, 62, C_PORT)

    sh.rect(114, 0, 232, 70, C_PORT, 'SYSTEM I/O EXPANDER TCA9535 (I2C0 0x20)')
    sh.place('Interface_Expansion:TCA9535PWR', 'U9', 'TCA9535PWR', 150, 34, 0, refpos=(142, 12, 'left'),
             valpos=(142, 13, 'left'))
    sh.tie('U9', ['3', '2', '21'], 'GND')
    sh.nets('U9', {'21': 'GND', '2': 'GND', '3': 'GND', '12': 'GND', '24': '+3V3', '22': 'I2C0_SCL',
                   '23': 'I2C0_SDA', '1': 'EXP_INT_N', '4': 'PORT1_OFF', '5': 'PORT2_OFF', '6': 'PORT3_OFF',
                   '7': 'PORT4_OFF', '8': 'PORT5_OFF', '9': 'CHG_CD', '10': 'USB_ILIM_1A5', '11': 'USB_ILIM_3A0',
                   '13': 'PORT1_FLT_N', '14': 'PORT2_FLT_N', '15': 'PORT3_FLT_N', '16': 'PORT4_FLT_N',
                   '17': 'PORT5_FLT_N', '18': 'USBIN_FLT_N', '19': 'CHG_PG_N', '20': 'BUCK_PG'}, L=2)
    C(sh, '100nF', 120, 8, '+3V3', 'GND', extra=V50)
    for i in range(5):
        R(sh, '100k', 170 + 4 * i, 8, '+3V3', 'PORT%d_OFF' % (i + 1))
        R(sh, '10k', 170 + 4 * i, 20, '+3V3', 'PORT%d_FLT_N' % (i + 1))
    for i, nn in enumerate(('USBIN_FLT_N', None, 'CHG_PG_N', 'BUCK_PG')):
        if nn is None:
            skip('R')
            continue
        R(sh, '10k', 192 + 4 * i, 8, '+3V3', nn)
    sh.notes(['Reset state (all inputs): P00-P04 PORTn_OFF 100k up -> ports OFF; P05 CHG_CD 10k up (power sheet)',
              '-> charging OFF; P06/P07 USB_ILIM_1A5/3A0 100k down at the leg FETs -> U_IN 0.50 A.',
              'P10-P14 port FLT, P15 USBIN_FLT_N, P16 CHG_PG_N, P17 BUCK_PG: inputs, 10k pull-ups. INT -> GPIO48.'],
             116, 62, C_PORT)

    # ---- 5 ports
    for i in range(5):
        n = i + 1
        x0 = 2 + 46 * i
        big = (n == 5)
        sh.rect(x0 - 2, 72, x0 + 44, 156, C_PORT,
                'PORT %d: J%d 5V %s' % (n, n, 'GH6 E0002, 2.0 A' if big else 'GH4 E0001, 0.87 A'))
        u = 'U%d' % (9 + n)
        sh.place('E0005:TPS259470L', u, 'TPS259470ARPW', x0 + 24, 98, 0, refpos=(x0 + 17, 89, 'left'),
                 valpos=(x0 + 17, 90, 'left'))
        P = 'PORT%d' % n
        sh.nets(u, {'5': 'V5', '6': 'V5_%d' % n, '1': P + '_EN', '2': P + '_OVLO', '7': P + '_DVDT',
                    '4': P + '_FLT_N', '3': None, '9': P + '_ILM', '10': P + '_ITIMER', '8': 'GND'}, L=2)
        divider(sh, '1M 1%', '365k 1%', x0 + 1, 78, 'V5', P + '_EN', 'GND')
        divider(sh, '1M 1%', '249k 1%', x0 + 12, 78, 'V5', P + '_OVLO', 'GND')
        fet(sh, 'Q%d' % (2 + n), x0 + 4, 108, P + '_OFF', P + '_EN', 'GND')
        C(sh, '1.8nF', x0 + 10, 116, P + '_DVDT', 'GND', extra=V50)
        C(sh, '22nF', x0 + 15, 116, P + '_ITIMER', 'GND', extra=V50)
        R(sh, '1.65k 1%' if big else '3.83k 1%', x0 + 20, 116, P + '_ILM', 'GND')
        C(sh, '10uF', x0 + 25, 116, 'V5', 'GND', fp=C0805, extra=V25)
        dtv = nref('D')
        sh.place('Diode:SMF5V0A', dtv, 'SMF5.0A', x0 + 32, 108, 270, fp='Diode_SMD:D_SOD-123F',
                 refpos=(x0 + 33.5, 107.5, 'left'), valpos=(x0 + 33.5, 108.5, 'left'))
        sh.net(dtv, '1', 'V5_%d' % n)
        sh.net(dtv, '2', 'GND')
        R(sh, '220R', x0 + 6, 128, P + '_SCL', P + '_SCL_C', horiz=True, L=2)
        R(sh, '220R', x0 + 6, 132, P + '_SDA', P + '_SDA_C', horiz=True, L=2)
        esd = nref('D')
        sh.place('Power_Protection:TPD2E2U06DRL', esd, 'TPD2E2U06DRL', x0 + 22, 136, 0,
                 refpos=(x0 + 25, 132, 'left'), valpos=(x0 + 25, 133, 'left'))
        sh.nets(esd, {'3': P + '_SCL_C', '5': P + '_SDA_C', '4': 'GND', '1': None, '2': None}, L=2)
        j = 'J%d' % n
        if big:
            sh.place('Connector_Generic_MountingPin:Conn_01x06_MountingPin', j, 'SM06B-GHS-TB', x0 + 38, 128, 0,
                     fp='Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal', refpos=(x0 + 38, 121, None),
                     valpos=(x0 + 38, 122, None), desc='E0002 port (5 V): 1,2 +5V 3 SCL 4 SDA 5,6 GND')
            sh.tie(j, ['5', '6'], 'GND')
            sh.tie(j, ['1', '2'], 'V5_5')
            sh.nets(j, {'1': 'V5_5', '2': 'V5_5', '3': P + '_SCL_C', '4': P + '_SDA_C', '5': 'GND', '6': 'GND',
                        'MP': 'GND'}, L=2)
        else:
            sh.place('Connector_Generic_MountingPin:Conn_01x04_MountingPin', j, 'SM04B-GHS-TB', x0 + 38, 128, 0,
                     fp='Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal', refpos=(x0 + 38, 122, None),
                     valpos=(x0 + 38, 123, None), desc='E0001 port (5 V): 1 +5V 2 SCL 3 SDA 4 GND')
            sh.nets(j, {'1': 'V5_%d' % n, '2': P + '_SCL_C', '3': P + '_SDA_C', '4': 'GND', 'MP': 'GND'}, L=2)
        sh.notes(['Silkscreen: "5V" + "%d" + "%s"' % (n, 'E0002' if big else 'E0001'),
                  'I_LIM %s; OVLO 6.02/5.47 V; UVLO 4.49/4.08 V' % ('2.03 A (1.80-2.20)' if big else '0.87 A (0.74-1.00)')],
                 x0, 151, C_PORT)
    sh.rect(234, 72, 262, 156, C_PORT, 'V5 BULK')
    C(sh, '47uF', 240, 90, 'V5', 'GND', fp=C1210, extra=V16)
    C(sh, '47uF', 246, 90, 'V5', 'GND', fp=C1210, extra=V16)
    sh.notes(['2 x 47 uF/16 V on V5', 'next to the eFuse group', '(+4 at the buck output).'], 236, 100, C_PORT)
    return sh


# ------------------------------------------------------------------ purchasing fields
import csv
E0003 = '/home/karpulis/KiCad/E0003 - ESP32 control box mainboard'   # reference data (read only)
MPN_BY_REF = {'U1': 'ESP32-S3-WROOM-1-N16R2', 'U2': 'BQ25887RGET', 'U4': 'USBLC6-2SC6',
              'U5': 'TPS629210DRLR', 'U6': 'S-8252AAG-M6T1U', 'U8': 'PCA9548APW,118',
              'U9': 'TCA9535PWR', 'U15': 'MAX17205G+T', 'U17': 'TPS56637RPAR', 'J10': 'FH12-18S-0.5SH(55)',
              'J11': 'USB4105-GF-A', 'L1': 'SRP7028A-2R2M', 'L2': 'IHLP2525CZER1R0M01', 'L3': 'DFE252012PD-2R2M=P2', 'F1': '0452010.MRL', 'Q1': 'PSMN2R0-30YLDX',
              'Q2': 'PSMN2R0-30YLDX', 'BH1': '1121', 'BH2': '1121', 'RT1': '103AT-2', 'RT2': '103AT-2'}
MPN_BY_VALUE = {   # (value, footprint fragment[, voltage]) -> MPN
    ('0R', 'R_0402'): 'RC0402JR-070RL', ('33R', 'R_0402'): 'RC0402FR-0733RL', ('100R', 'R_0402'): 'RC0402FR-07100RL',
    ('150R', 'R_0402'): 'RC0402FR-07150RL', ('220R', 'R_0402'): 'RC0402FR-07220RL', ('1k', 'R_0402'): 'RC0402FR-071KL',
    ('1.65k 1%', 'R_0402'): 'RC0402FR-071K65L', ('2.2k', 'R_0402'): 'RC0402FR-072K2L',
    ('3.83k 1%', 'R_0402'): 'RC0402FR-073K83L', ('4.7k', 'R_0402'): 'RK73H1ETTP4701F',
    ('8.2k 1%', 'R_0402'): 'RC0402FR-078K2L', ('10k', 'R_0402'): 'RC0402FR-0710KL',
    ('10k 1%', 'R_0402'): 'RC0402FR-0710KL', ('100k', 'R_0402'): 'RC0402FR-07100KL',
    ('137k 1%', 'R_0402'): 'RC0402FR-07137KL', ('232k 1%', 'R_0402'): 'RC0402FR-07232KL',
    ('1M 1%', 'R_0402'): 'RC0402FR-071ML', ('1M', 'R_0402'): 'RC0402FR-071ML', ('5mR 1%', 'R_2512'): 'CRF2512-FZ-R005ELF',
    ('49.9R', 'R_0402'): 'RC0402FR-0749R9L', ('160R', 'R_0402'): 'RC0402FR-07160RL', ('261R', 'R_0402'): 'RC0402FR-07261RL',
    ('470R', 'R_0402'): 'RC0402FR-07470RL', ('2k', 'R_0402'): 'RK73H1ETTP2001F', ('5.23k 1%', 'R_0402'): 'RC0402FR-075K23L',
    ('21.5k 1%', 'R_0402'): 'RC0402FR-0721K5L', ('27.4k 1%', 'R_0402'): 'RC0402FR-0727K4L',
    ('30.1k 1%', 'R_0402'): 'RC0402FR-0730K1L',
    # new in E0005 (DigiKey checked 2026-10-27, bom/new_parts_digikey.csv)
    ('5.1k 1%', 'R_0402'): 'RC0402FR-075K1L', ('390k 1%', 'R_0402'): 'RC0402FR-07390KL',
    ('249k 1%', 'R_0402'): 'RC0402FR-07249KL', ('365k 1%', 'R_0402'): 'RC0402FR-07365KL',
    ('6.65k 1%', 'R_0402'): 'RC0402FR-076K65L', ('2.32k 1%', 'R_0402'): 'RC0402FR-072K32L',
    ('374R 1%', 'R_0402'): 'RC0402FR-07374RL', ('300R', 'R_0402'): 'RC0402FR-07300RL',
    ('39R 1% 1W', 'R_2512'): 'RMCF2512FT39R0', ('69.8k 1%', 'R_0402'): 'RC0402FR-0769K8L',
    ('200k 1%', 'R_0402'): 'RC0402FR-07200KL', ('53.6k 1%', 'R_0402'): 'RC0402FR-0753K6L',
    ('20k', 'R_0402'): 'RC0402FR-0720KL', ('39k', 'R_0402'): 'RC0402FR-0739KL', ('100k', 'R_0402'): 'RC0402FR-07100KL',
    ('100pF', 'C_0402'): 'GRM1555C1H101JA01D', ('AO3401A', 'SOT-23'): 'AO3401A', ('SMF5.0A', 'SOD-123F'): 'SMF5.0A',
    ('TPD1E10B09', 'D_0402'): 'TPD1E10B09DPYR',
    ('100nF', 'C_0402'): 'GRM155R71H104KE14D',   # one 50 V part for all (C7 sits on VBUS)
    ('1uF', 'C_0402'): 'CL05A105KP5NNNC', ('1uF', 'C_0603'): 'C1608X7R1H105K080AB', ('1.8nF', 'C_0402'): 'C0402C182K5RACTU',
    ('22nF', 'C_0402'): 'GRM155R71H223KA12D', ('4.7nF', 'C_0402'): 'GRM155R71H472KA01J', ('1nF', 'C_0402'): 'GRM155R71H102KA01D',
    ('47nF', 'C_0402'): 'GRM155R71H473KE14D', ('0.47uF', 'C_0402'): 'GRM155R61A474KE15D',
    ('4.7uF', 'C_0603'): 'GRM188R61E475KE11D', ('10uF', 'C_0805'): 'TMK212BBJ106MG-T', ('22uF', 'C_0805'): 'CL21A226KQCLRNC',
    ('47uF', 'C_1210'): 'CL32A476KOJNNNE',
    ('2N7002', 'SOT-23'): '2N7002-7-F', ('TVS2200DRVR', 'WSON'): 'TVS2200DRVR', ('SMF9.0A', 'SOD-123F'): 'SMF9.0A',
    ('TPD2E2U06DRL', 'SOT-553'): 'TPD2E2U06DRLR', ('PESD5V0L1UL', 'SOD-882'): 'PESD5V0L1UL,315',
    ('BAT54W', 'SOT-323'): 'BAT54W,135', ('TPS259470ARPW', 'RPW'): 'TPS259470ARPWR',   # auto-retry (Manager 2026-10-18)
    ('SM02B-GHS-TB', 'GH'): 'SM02B-GHS-TB', ('SM04B-GHS-TB', 'GH'): 'SM04B-GHS-TB', ('SM06B-GHS-TB', 'GH'): 'SM06B-GHS-TB(LF)(SN)',
    ('PWR', 'PTS810'): 'PTS810SJM250SMTR LFS', ('BOOT', 'PTS810'): 'PTS810SJM250SMTR LFS',
    ('RESET', 'PTS810'): 'PTS810SJM250SMTR LFS', ('green', 'LED'): 'LTST-C191KGKT', ('amber', 'LED'): 'LTST-C191KSKT',
    ('red', 'LED'): 'LTST-C191KRKT'}
PN_FALLBACK = {'AO3401A': ('Alpha & Omega Semiconductor Inc.', 'DigiKey', '785-1001-1-ND'),
               'RC0402FR-0720KL': ('YAGEO', 'DigiKey', '311-20.0KLRCT-ND'),
               'RC0402FR-0739KL': ('YAGEO', 'DigiKey', '311-39.0KLRCT-ND'),'GRM155R71H473KE14D': ('Murata Electronics', 'DigiKey', '490-10702-1-ND'),
               'SM06B-GHS-TB(LF)(SN)': ('JST Sales America Inc.', 'DigiKey', '455-1568-1-ND'),
               'TPS259470ARPWR': ('Texas Instruments', 'DigiKey', '296-TPS259470ARPWRCT-ND')}
NEW_MFR = {'RC04': 'YAGEO', 'GRM1': 'Murata Electronics', 'BAT5': 'Diodes Incorporated'}


def assign_fields(sheets):
    """Add MPN / Manufacturer / Supplier / Supplier PN from E0003's checked BOM + bom/new_parts_digikey.csv."""
    from sch_core import prop as _prop
    rows = {r['MPN']: r for r in csv.DictReader(open(os.path.join(E0003, 'bom', 'E0003_digikey_bom.csv')))}
    fab_bom = os.path.join(E0003, 'fab', 'E0003_revA', 'E0003_revA_BOM.csv')   # E0003's released BOM wins
    if os.path.exists(fab_bom):
        rows.update({r['MPN']: r for r in csv.DictReader(open(fab_bom)) if r.get('MPN')})
    rows.update({r['MPN']: dict(r, Supplier='DigiKey') for r in
                 csv.DictReader(open(os.path.join(PROJ, 'bom', 'new_parts_digikey.csv'))) if r['Stock'] != '0'})
    report = set()
    for sh in sheets:
        for s in sh.symbols:
            if str(s[1][1]).startswith('power:'):
                continue
            flags = {x[0]: x[1] for x in s if isinstance(x, list) and len(x) == 2 and not isinstance(x[1], list)}
            if flags.get('in_bom') == 'no':
                continue
            props = {p[1]: p for p in s if isinstance(p, list) and p and p[0] == 'property'}
            ref, val, fp = props['Reference'][2], props['Value'][2], props['Footprint'][2]
            volt = props['Voltage'][2] if 'Voltage' in props else ''
            mpn = MPN_BY_REF.get(ref)
            if not mpn:
                for k, v in MPN_BY_VALUE.items():
                    if k[0] == val and k[1] in fp and (len(k) < 3 or k[2] == volt):
                        mpn = v
                        break
            if not mpn:
                report.add('no MPN: %s %s %s' % (ref, val, fp))
                continue
            r = rows.get(mpn, {})
            if not r and mpn in PN_FALLBACK:
                f = PN_FALLBACK[mpn]
                r = {'Manufacturer': f[0], 'Supplier': f[1], 'SupplierPN': f[2]}
            if not r:
                report.add('not in Parts BOM yet: %s (%s)' % (mpn, val))
            mfr = r.get('Manufacturer') or NEW_MFR.get(mpn[:4], '')
            sup, spn = r.get('Supplier') or 'DigiKey', r.get('SupplierPN', '')
            at = [x for x in s if isinstance(x, list) and x and x[0] == 'at'][0]
            idx = max(i for i, x in enumerate(s) if isinstance(x, list) and x and x[0] == 'property')
            for k, v in reversed((('MPN', mpn), ('Manufacturer', mfr), ('Supplier', sup), ('Supplier PN', spn))):
                s.insert(idx + 1, _prop(k, v, at[1], at[2], 0, hide=True))
    return report


def main():
    sheets = [sheet_power(), sheet_battery(), sheet_mcu(), sheet_ports()]
    for m in sorted(assign_fields(sheets)):
        print('  BOM field:', m)
    write_all(PROJ, 'E0005 ESP32-S3 5 V controller', 'A', '2026-10-27',
              ['5 V USB-C (no PD), U_IN eFuse, BQ25887 2S charger, TPS56637 2S -> 5 V buck, MAX17205, 5 x 5 V ports',
               'Spec docs/SPEC.md v1.0; generated by build/scripts/gen_sch.py'], sheets)
    n = sum(len([s for s in sh.symbols if not str(s[1][1]).startswith('power:')]) for sh in sheets)
    print('wrote', len(sheets), 'sheets,', n, 'symbols')


if __name__ == '__main__':
    main()
