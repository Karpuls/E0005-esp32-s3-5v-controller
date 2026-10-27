#!/usr/bin/env python3
"""Generate the E0003 control box mainboard schematic (root + 4 hierarchical sheets).

Run:  python3 build/scripts/gen_sch.py   (then build/scripts/render_check.sh)
Spec: docs/SPEC.md v1.2. Notes: docs/schematic_notes.md.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from sch_core import Sheet, write_all, G, C_PWR, C_BAT, C_MCU, C_PORT, C_UI
import sch_core

# MID and SNS_P were cross-sheet (test pads) when the board was laid out: keep their global names.
sch_core.FORCE_GLOBAL.update({'MID', 'SNS_P'})

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

cnt = {}

def nref(prefix):
    cnt[prefix] = cnt.get(prefix, 0) + 1
    return '%s%d' % (prefix, cnt[prefix])

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

def divider(sh, vt, vb, x, y, ntop, nmid, nbot, side='right', L=2):
    """Vertical divider: top R at y, bottom R at y+5, mid node wired out to a label."""
    rt = R(sh, vt, x, y, ntop, None)
    rb = R(sh, vb, x, y + 5, None, nbot)
    a, b = sh.pin(rt, '2'), sh.pin(rb, '1')
    sh.wire(a, b)
    m = (x * G, (y + 2.5) * G)
    sh.junction(m)
    q = ((x + (L if side == 'right' else -L)) * G, m[1])
    sh.wire(m, q)
    sh.label(nmid, q, side)
    return rt, rb

def r_led(sh, x, y, n_in, n_k, color, rval='1k'):
    """Horizontal R then LED (anode side towards the R), wired directly."""
    r = R(sh, rval, x, y, n_in, None, horiz=True)
    d = nref('D')
    sh.place('Device:LED_Small', d, color, x + 4, y, 180, fp=LED0603, refpos=(x + 4, y - 1.1, None),
             valpos=(x + 4, y + 1.2, None))
    sh.wire(sh.pin(r, '2'), sh.pin(d, '2'))
    sh.net(d, '1', n_k)
    return d

def fet(sh, ref, x, y, g, d, s, lib='Transistor_FET:2N7002', val='2N7002'):
    sh.place(lib, ref, val, x, y, 0, refpos=(x + 1, y - 0.5, 'left'), valpos=(x + 1, y + 0.5, 'left'))
    sh.net(ref, '1', g)
    sh.net(ref, '2', s)
    sh.net(ref, '3', d)

# =====================================================================================
# Sheet 2: power input, USB-PD, charger, 3V3
# =====================================================================================
def sheet_power():
    sh = Sheet('Power input, PD, charger, 3V3', 'power.kicad_sch', page=2, size=(520, 380))
    sh.rect(0, 0, 62, 56, C_PWR, 'USB-C J11, VBUS TVS, USB ESD')
    sh.place('Connector:USB_C_Receptacle_USB2.0_16P', 'J11', 'USB4105-GF-A', 12, 22, 0,
             fp='Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
             refpos=(4, 7, 'left'), valpos=(4, 8, 'left'),
             desc='USB 2.0 Type-C receptacle, 16-pin, 5 A / 20 V, west edge')
    sh.nets('J11', {'A4': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS', 'B9': 'VBUS', 'A5': 'CC1', 'B5': 'CC2',
                    'A6': 'USB_DP_C', 'B6': 'USB_DP_C', 'A7': 'USB_DN_C', 'B7': 'USB_DN_C',
                    'A8': None, 'B8': None, 'A1': 'GND', 'A12': 'GND', 'B1': 'GND', 'B12': 'GND',
                    'SH': 'USB_SHIELD'}, L=2)
    R(sh, '1M', 6, 46, 'USB_SHIELD', 'GND')
    C(sh, '4.7nF', 10, 46, 'USB_SHIELD', 'GND', extra=V50)
    sh.notes(['Shell: 1M || 4.7nF to GND.'], 2, 51.5)
    dt = nref('D')
    sh.place('Power_Protection:TVS2200DRV', dt, 'TVS2200DRVR', 40, 10, 0, refpos=(44, 8, 'left'),
             valpos=(44, 9, 'left'))
    sh.nets(dt, {'4': 'VBUS', '5': 'VBUS', '6': 'VBUS', '1': 'GND', '2': 'GND', '3': 'GND', '7': 'GND'})
    C(sh, '1uF', 52, 10, 'VBUS', 'GND', fp=C0603, extra=V50)
    sh.place('Power_Protection:USBLC6-2SC6', 'U4', 'USBLC6-2SC6', 42, 34, 0, refpos=(46, 29, 'left'),
             valpos=(46, 30, 'left'))
    sh.nets('U4', {'1': 'USB_DP_C', '6': 'USB_DP_C', '3': 'USB_DN_C', '4': 'USB_DN_C', '5': '+3V3', '2': 'GND'}, L=2)
    R(sh, '0R', 44, 46, 'USB_DP_C', 'USB_DP', horiz=True, L=2)
    R(sh, '0R', 44, 51, 'USB_DN_C', 'USB_DN', horiz=True, L=2)
    sh.notes(['USBLC6 VBUS pin to +3V3 (VBUS reaches 15 V).', 'D+/D- 90 ohm diff., 0R footprints to GPIO20/19.'],
             2, 53)

    # ---- STUSB4500
    sh.rect(0, 58, 62, 124, C_PWR, 'USB-PD SINK STUSB4500 (I2C0 0x28), PDO 15 V / 9 V / 5 V')
    sh.place('Interface_USB:STUSB4500QTR', 'U3', 'STUSB4500QTR', 24, 88, 0, refpos=(17, 72, 'left'),
             valpos=(17, 73, 'left'), fp='Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm')
    sh.tie('U3', ['12', '13'], 'GND')
    sh.nets('U3', {'1': 'CC1', '2': 'CC1', '4': 'CC2', '5': 'CC2', '3': None, '6': 'PD_RESET', '7': 'I2C0_SCL',
                   '8': 'I2C0_SDA', '9': None, '10': 'GND', '25': 'GND', '11': None, '12': 'GND', '13': 'GND',
                   '14': None, '15': None, '16': None, '17': None, '18': 'PD_VSDISCH', '19': 'PD_ALERT_N',
                   '20': None, '21': 'PD_1V2', '22': 'GND', '23': 'PD_2V7', '24': 'VBUS'}, L=2)
    R(sh, '100k', 50, 92, 'PD_RESET', 'GND')
    R(sh, '1k', 50, 78, 'VBUS', 'PD_VSDISCH')
    C(sh, '1uF', 54, 92, 'PD_1V2', 'GND')
    C(sh, '1uF', 58, 92, 'PD_2V7', 'GND')
    sh.notes(['ADDR0/1 = GND -> 0x28. RESET 100k to GND. VSYS = GND (powered from VBUS only).',
              'NVM (write once): PDO1 5 V, PDO2 9 V >= 2 A, PDO3 15 V >= 2 A, REQ_SRC_CURRENT = 1.',
              'Open-drain flags ATTACH/POWER_OKx/GPIO/A_B_SIDE/VBUS_EN_SNK and DISCH unused.'], 2, 118)

    # ---- BQ25798
    sh.rect(64, 0, 186, 86, C_PWR, 'CHARGER / POWER PATH BQ25798 (I2C0 0x6B), 2S, 750 kHz')
    sh.place('Battery_Management:BQ25798', 'U2', 'BQ25798RQMR', 110, 42, 0, refpos=(103, 18, 'left'),
             valpos=(103, 19, 'left'))
    sh.tie('U2', ['10', '11'], 'GND')
    sh.nets('U2', {'2': 'VBUS', '3': 'VBUS', '8': 'VBUS', '9': 'VBUS', '10': 'GND', '11': 'GND', '27': 'GND',
                   '6': None, '7': None, '29': 'PMID', '28': 'CHG_SW1', '26': 'CHG_SW2', '4': 'CHG_BTST1', '19': 'CHG_BTST2',
                   '5': 'REGN', '25': 'VSYS', '22': 'BAT+', '23': 'BAT+', '18': 'BATP', '20': 'CHG_PROG',
                   '17': 'ILIM_HIZ', '16': 'CHG_TS', '13': 'CHG_CE_N', '12': 'CHG_QON_N', '14': 'I2C0_SCL',
                   '15': 'I2C0_SDA', '21': 'CHG_INT_N', '1': 'CHG_STAT', '24': 'SDRV'}, L=2)
    # input / PMID caps
    for i in range(2):
        C(sh, '10uF', 68 + 3 * i, 8, 'VBUS', 'GND', fp=C0805, extra=V25)
    C(sh, '100nF', 74, 8, 'VBUS', 'GND', extra=V50)
    for i in range(3):
        C(sh, '10uF', 80 + 3 * i, 8, 'PMID', 'GND', fp=C0805, extra=V25)
    # inductor + bootstrap
    sh.place('Device:L', 'L1', '2.2uH', 150, 8, 90, fp='Inductor_SMD:L_Bourns_SRP7028A_7.3x6.6mm',
             refpos=(150, 6.5, None), valpos=(150, 9.6, None),
             desc='2.2 uH, Isat 14 A, 20 mOhm, shielded (charger buck-boost)')
    sh.net('L1', '1', 'CHG_SW1', 2)
    sh.net('L1', '2', 'CHG_SW2', 2)
    C(sh, '47nF', 160, 8, 'CHG_BTST1', 'CHG_SW1', extra=V50)
    C(sh, '47nF', 165, 8, 'CHG_BTST2', 'CHG_SW2', extra=V50)
    # SYS / BAT caps
    for i in range(5):
        C(sh, '10uF', 140 + 3 * i, 22, 'VSYS', 'GND', fp=C0805, extra=V25)
    for i in range(2):
        C(sh, '10uF', 140 + 3 * i, 33, 'BAT+', 'GND', fp=C0805, extra=V25)
    R(sh, '100R', 152, 33, 'BAT+', 'BATP')
    # REGN, PROG, ILIM_HIZ, TS, SDRV, STAT, CE
    C(sh, '4.7uF', 140, 46, 'REGN', 'GND', fp=C0603, extra=V25)
    R(sh, '8.2k 1%', 145, 46, 'CHG_PROG', 'GND')
    divider(sh, '10k 1%', '21.5k 1%', 150, 44, 'REGN', 'ILIM_HIZ', 'GND')
    divider(sh, '5.23k 1%', '30.1k 1%', 158, 44, 'REGN', 'CHG_TS', 'GND')
    C(sh, '1nF', 164, 46, 'SDRV', 'GND', extra=V50)
    R(sh, '10k', 170, 44, '+3V3', 'CHG_CE_N')
    r_led(sh, 142, 60, '+3V3', 'CHG_STAT', 'amber')
    sh.notes(['PROG 8.2k: 2S, 750 kHz. ILIM_HIZ = 5 V x 21.5/31.5 = 3.41 V -> IINDPM clamp 3.0 A;',
              '  BQ29209 OV2 FET (battery sheet) pulls ILIM_HIZ < 0.75 V -> HIZ.',
              'TS: REGN 5.23k / 30.1k || NTC1 (103AT-2, battery sheet) -> JEITA 0-60 C.',
              'CE: 10k pull-up -> charging OFF at reset; TCA9535 P05 enables. QON <- power button.',
              'VAC1 = VAC2 = VBUS, ACDRV1/2 = GND: single input, no ACFET (datasheet Table 7-5).',
              'D+/D- not used (IINDPM set by firmware from the STUSB4500 contract). SDRV: 1 nF (no ship FET).'],
             66, 68, C_PWR)

    # ---- 3V3 buck
    sh.rect(64, 88, 186, 124, C_PWR, '3V3 BUCK TPS629210 (from VSYS, 1 A)')
    sh.place('E0003:TPS629210', 'U5', 'TPS629210DRL', 100, 104, 0, refpos=(90, 98, 'left'),
             valpos=(90, 99, 'left'))
    sh.nets('U5', {'6': 'VSYS', '7': 'VSYS', '8': 'BUCK_MODE', '1': None, '2': None, '4': 'BUCK_SW',
                   '5': 'GND'}, L=2)
    vos = sh.pin('U5', '3')
    corner = (vos[0] + 3 * G, vos[1])
    sh.wire(vos, corner, (corner[0], corner[1] + 2 * G))
    sh.power('+3V3', (corner[0], corner[1] + 2 * G), flip=True)
    C(sh, '4.7uF', 70, 104, 'VSYS', 'GND', fp=C0603, extra=V25)
    C(sh, '100nF', 74, 104, 'VSYS', 'GND', extra=V50)
    R(sh, '27.4k 1%', 80, 112, 'BUCK_MODE', 'GND')
    sh.place('Device:L', 'L3', '2.2uH', 122, 102, 90, fp='Inductor_SMD:L_1008_2520Metric',
             refpos=(122, 100.5, None), valpos=(122, 103.6, None))
    sh.net('L3', '1', 'BUCK_SW', 2)
    sh.net('L3', '2', '+3V3', 2)
    C(sh, '22uF', 132, 104, '+3V3', 'GND', fp=C0805, extra={'Voltage': '6.3V'})
    sh.flag('+3V3', 140, 101)
    sh.notes(['MODE/S-CONF 27.4k: VSET mode, auto PFM/PWM, output discharge.',
              'FB/VSET open (>= 249k) -> 3.3 V. EN tied to VSYS. PG unused.'], 66, 118, C_PWR)
    sh.flag('VBUS', 30, 2)
    sh.flag('GND', 36, 2)
    return sh

# =====================================================================================
# Sheet 3: battery pack, protection, balancing, gauge
# =====================================================================================
def sheet_battery():
    sh = Sheet('Battery pack, protection, balancing, gauge', 'battery.kicad_sch', page=3, size=(520, 380))
    sh.rect(0, 0, 70, 70, C_BAT, 'CELLS (bottom side), F1, REVERSE-CELL LEDS, NTCs')
    MECH = 'E0003_mech:Keystone_1121_1x21700_THM'
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
    # reverse-cell indicators: lit only when a cell is inserted reversed
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
             fp='E0003:NTC_Leaded_THT_P2.54mm_Drill0.8mm', refpos=(9.5, 59, 'left'), valpos=(9.5, 60, 'left'),
             desc='NTC 10k B3435 Semitec 103AT-2 leaded bead, bonded to the cans (charger TS)')
    sh.net('RT1', '1', 'CHG_TS')
    sh.net('RT1', '2', 'GND')
    sh.place('Device:Thermistor_NTC', 'RT2', '10k B3435', 22, 60, 0,
             fp='E0003:NTC_Leaded_THT_P2.54mm_Drill0.8mm', refpos=(23.5, 59, 'left'), valpos=(23.5, 60, 'left'),
             desc='NTC 10k B3435 Semitec 103AT-2 leaded bead, bonded to the cans (gauge AIN1)')
    sh.net('RT2', '1', 'GAUGE_AIN1')
    sh.net('RT2', '2', 'GND')
    sh.notes(['RT1 -> charger TS, RT2 -> gauge AIN1; both between the cells.'], 2, 67)

    # ---- protection
    sh.rect(72, 0, 186, 70, C_BAT, 'PRIMARY PROTECTION S-8252AAG + LOW-SIDE FETS, R_SENSE')
    sh.place('E0003:S-8252', 'U6', 'S-8252AAG-M6T1U', 100, 30, 0, refpos=(93, 24, 'left'), valpos=(93, 25, 'left'))
    sh.nets('U6', {'5': 'S8252_VDD', '4': 'S8252_VC', '6': 'B_N', '1': 'DSG_G', '2': 'CHG_G', '3': 'S8252_VM'}, L=2)
    R(sh, '470R', 80, 12, 'CELL2_P', 'S8252_VDD')
    R(sh, '470R', 85, 12, 'MID', 'S8252_VC')
    C(sh, '100nF', 80, 26, 'S8252_VDD', 'S8252_VC', extra=V50)
    C(sh, '100nF', 85, 26, 'S8252_VC', 'B_N', extra=V50)
    schottky(sh, 80, 46, 'S8252_VC', 'S8252_VDD', horiz=False)
    schottky(sh, 85, 46, 'B_N', 'S8252_VC', horiz=False)
    R(sh, '2k', 120, 22, 'S8252_VM', 'GND')
    sh.place('E0003:PSMN2R0-30YLDX', 'Q1', 'PSMN2R0-30YLDX', 132, 40, 0, refpos=(134, 36, 'left'),
             valpos=(134, 37, 'left'), desc='Discharge FET (cell side), 30 V 2 mOhm LFPAK56')
    sh.place('E0003:PSMN2R0-30YLDX', 'Q2', 'PSMN2R0-30YLDX', 150, 40, 0, refpos=(152, 36, 'left'),
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
              'R1/R2 470R + C 100nF per ABLIC Table 11; R3 2k on VM. BAT54W clamps: reverse-cell protection of VC.'],
             74, 60, C_BAT)

    # ---- balancer / OV2
    sh.rect(0, 72, 92, 124, C_BAT, 'BALANCER + SECONDARY OV BQ29209 (OV 4.30 V)')
    sh.place('E0003:BQ29209', 'U7', 'BQ29209DRB', 44, 96, 0, refpos=(37, 86, 'left'), valpos=(37, 87, 'left'))
    sh.nets('U7', {'1': 'BQ_VC2', '2': 'BQ_VC1', '3': 'BQ_VC1CB', '4': 'BQ_CD', '7': 'BQ_VDD', '5': 'B_N',
                   '9': 'B_N', '8': 'BQ_OUT', '6': 'BQ_CB_EN_N'}, L=2)
    R(sh, '160R', 6, 80, 'CELL2_P', 'BQ_VC2')
    R(sh, '261R', 11, 80, 'MID', 'BQ_VC1')
    R(sh, '100R', 16, 80, 'MID', 'BQ_VC1CB')
    C(sh, '100nF', 6, 95, 'BQ_VC2', 'BQ_VC1', extra=V50)
    C(sh, '100nF', 11, 95, 'BQ_VC1', 'B_N', extra=V50)
    C(sh, '100nF', 16, 95, 'BQ_CD', 'B_N', extra=V50)
    R(sh, '100R', 21, 80, 'CELL2_P', 'BQ_VDD')
    C(sh, '100nF', 26, 80, 'BQ_VDD', 'B_N', extra=V50)
    schottky(sh, 21, 106, 'BQ_VC1', 'BQ_VC2', horiz=False)
    schottky(sh, 26, 106, 'B_N', 'BQ_VC1', horiz=False)
    R(sh, '100k', 60, 84, 'BQ_VDD', 'BQ_CB_EN_N')
    fet(sh, 'Q10', 62, 96, 'BAL_EN', 'BQ_CB_EN_N', 'B_N')
    R(sh, '100k', 54, 104, 'BAL_EN', 'B_N')
    R(sh, '1k', 70, 106, 'BQ_OUT', 'OV2_G', horiz=True)
    fet(sh, 'Q8', 80, 96, 'OV2_G', 'ILIM_HIZ', 'GND')
    fet(sh, 'Q9', 80, 110, 'OV2_G', 'OV2_N', 'GND')
    sh.notes(['Values per BQ29209 Fig. 9 (260R -> 261R E96). CD 0.1 uF -> ~0.9 s OV delay. CB_EN active-low (stack-referenced):',
              '100k to VDD = balancing OFF; Q10 (BAL_EN = TCA9535 P07, 100k gate pull-down) enables it.',
              'OUT high on cell OV (4.30 V): Q8 -> charger HIZ (ILIM_HIZ low), Q9 -> OV2_N to TCA9535 P15.'],
             2, 119, C_BAT)

    # ---- gauge
    sh.rect(94, 72, 186, 124, C_BAT, 'FUEL GAUGE MAX17205 (stack-only, board GND), MID ADC divider')
    sh.place('E0003:MAX17205', 'U15', 'MAX17205G+', 132, 98, 0, refpos=(125, 85, 'left'), valpos=(125, 86, 'left'))
    sh.tie('U15', ['7', '6', '13'], 'GND')
    sh.nets('U15', {'5': 'GAUGE_VBATT', '7': 'GND', '6': 'GND', '13': 'GND', '2': 'SNS_P', '4': 'GAUGE_CSN',
                    '12': 'GAUGE_SDA', '11': 'GAUGE_SCL', '8': 'GAUGE_ALRT', '14': 'GAUGE_THRM',
                    '9': 'GAUGE_AIN1', '10': 'GND', '1': 'GAUGE_REG3', '3': 'GAUGE_REG2', '15': 'GND'}, L=2)
    R(sh, '49.9R', 100, 78, 'BAT+', 'GAUGE_VBATT')
    C(sh, '100nF', 105, 84, 'GAUGE_VBATT', 'GND', extra=V50)
    sh.place('Device:NetTie_2', 'NT1', 'NetTie_2', 108, 112, 0, fp='NetTie:NetTie-2_SMD_Pad0.5mm',
             refpos=(108, 110.5, None), valpos=(108, 113.5, None), in_bom=False, hide_value=True,
             desc='Kelvin tap: gauge CSN to the GND pad of R_SENSE')
    sh.net('NT1', '1', 'GAUGE_CSN')
    sh.net('NT1', '2', 'GND')
    R(sh, '150R', 160, 80, 'GAUGE_SDA', 'I2C0_SDA', horiz=True, L=2)
    R(sh, '150R', 160, 84, 'GAUGE_SCL', 'I2C0_SCL', horiz=True, L=2)
    R(sh, '1k', 160, 88, 'GAUGE_ALRT', 'GAUGE_ALRT_N', horiz=True, L=2)
    R(sh, '10k 1%', 160, 96, 'GAUGE_THRM', 'GAUGE_AIN1')
    C(sh, '0.47uF', 166, 104, 'GAUGE_REG3', 'GND')
    C(sh, '0.47uF', 171, 104, 'GAUGE_REG2', 'GND')
    divider(sh, '1M 1%', '1M 1%', 176, 80, 'MID', 'VMID_SENSE', 'GND', side='left')
    C(sh, '100nF', 181, 84, 'VMID_SENSE', 'GND', extra=V50)
    sh.notes(['Per MAX17205 Fig. 2 (low-side protector): GND/EP = board GND, CELL1/2/X = GND, PackCfg BtEn=1, CxEn=0, ChEn=0.',
              'CSP = SNS_P (FET side of R_SENSE), CSN via NT1 Kelvin tap. VBATT 49.9R + 100 nF from BAT+.',
              'THRM -> 10k -> AIN1 + RT2. AIN2 unused (GND). I2C0 0x36/0x0B, 150R series; ALRT 1k -> GPIO35.',
              'MID divider 1M/1M + 100 nF -> GPIO4 (coarse cell-1 voltage, board-GND referenced).'],
             96, 116, C_BAT)
    for net, x in (('B_N', 46), ('S8252_VDD', 52), ('BQ_VDD', 58), ('GAUGE_VBATT', 64)):
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
                   '39': 'I2C1_SDA', '38': 'I2C1_SCL', '15': None, '4': 'VMID_SENSE', '5': 'CHG_INT_N',
                   '6': 'PD_ALERT_N', '7': 'EXP_INT_N', '12': 'I2C0_SDA', '17': 'I2C0_SCL', '18': 'LCD_CS',
                   '19': 'LCD_MOSI_MCU', '20': 'LCD_SCK_MCU', '21': 'LCD_MISO', '22': 'LCD_DC', '8': 'SW1',
                   '9': 'SW2', '10': 'SW3', '11': 'SW4', '13': 'USB_DN', '14': 'USB_DP', '23': 'PWR_BTN_N',
                   '28': 'GAUGE_ALRT_N', '29': 'SPARE36', '30': 'SPARE37', '31': 'MUX_RST_N', '32': 'LCD_RST',
                   '33': 'LED_STATUS', '34': 'LCD_SDCS', '35': 'TOUCH_INT_N', '37': None, '36': None,
                   '26': None, '16': None, '24': 'LCD_LITE', '25': None}, L=2)
    C(sh, '22uF', 6, 8, '+3V3', 'GND', fp=C0805, extra={'Voltage': '6.3V'})
    C(sh, '100nF', 10, 8, '+3V3', 'GND', extra=V50)
    # pull-ups
    for i, nn in enumerate(('EN', 'BOOT', 'GAUGE_ALRT_N', 'CHG_INT_N', 'PD_ALERT_N', 'EXP_INT_N', 'MUX_RST_N',
                            'TOUCH_INT_N', 'PWR_BTN_N')):
        R(sh, '10k', 72 + 3 * i if i < 8 else 72, 8 if i < 8 else 20, '+3V3', nn)
    R(sh, '2.2k', 72, 32, '+3V3', 'I2C0_SDA')
    R(sh, '2.2k', 76, 32, '+3V3', 'I2C0_SCL')
    C(sh, '1uF', 14, 8, 'EN', 'GND')
    sh.notes(['EN 10k / 1 uF RC. Strapping: GPIO0 BOOT 10k up; GPIO3, 45, 46 NC. No test points (owner rule).',
              'N16R2: quad PSRAM, GPIO35-37 usable (35 = gauge ALRT, 36/37 spare).',
              'I2C0 (system) 2.2k pull-ups here. Interrupt lines 10k pull-ups.'], 2, 120, C_MCU)
    # buttons + LED
    sh.place('Switch:SW_Push', 'SW2', 'BOOT', 88, 46, 90, fp='Button_Switch_SMD:SW_SPST_PTS810',
             refpos=(90, 45, 'left'), valpos=(90, 47, 'left'))
    sh.net('SW2', '1', 'BOOT')
    sh.net('SW2', '2', 'GND')
    sh.place('Switch:SW_Push', 'SW3', 'RESET', 88, 58, 90, fp='Button_Switch_SMD:SW_SPST_PTS810',
             refpos=(90, 57, 'left'), valpos=(90, 59, 'left'))
    sh.net('SW3', '1', 'EN')
    sh.net('SW3', '2', 'GND')
    r_led(sh, 80, 72, 'LED_STATUS', 'GND', 'green')

    # ---- power button
    sh.rect(98, 0, 186, 38, C_UI, 'POWER BUTTON (ship mode on/off) SW1 + J12')
    sh.place('Switch:SW_Push', 'SW1', 'PWR', 106, 18, 90, fp='Button_Switch_SMD:SW_SPST_PTS810',
             refpos=(108, 17, 'left'), valpos=(108, 19, 'left'))
    sh.net('SW1', '1', 'PB_RAW')
    sh.net('SW1', '2', 'GND')
    sh.place('Connector_Generic_MountingPin:Conn_01x02_MountingPin', 'J12', 'SM02B-GHS-TB', 120, 18, 0,
             fp='Connector_JST:JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal', refpos=(120, 14, None),
             valpos=(120, 23, None), desc='Panel power button, JST-GH 2-pin')
    sh.nets('J12', {'1': 'PB_RAW', '2': 'GND', 'MP': 'GND'}, L=2)
    de = nref('D')
    sh.place('Diode:PESD5V0L1UL', de, 'PESD5V0L1UL', 130, 18, 270, refpos=(131.5, 17.5, 'left'),
             valpos=(131.5, 18.5, 'left'))
    sh.net(de, '1', 'PB_RAW')
    sh.net(de, '2', 'GND')
    schottky(sh, 150, 12, 'CHG_QON_N', 'PB_RAW')
    schottky(sh, 150, 24, 'PWR_BTN_N', 'PB_RAW')
    sh.notes(['Press: BQ25798 QON low (exits ship mode) + GPIO21 low (wake). Long press -> firmware ship mode.'],
             100, 34, C_UI)

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
                    '17': 'EYESPI_GP1', '18': 'EYESPI_GP2', 'MP': 'GND'}, L=2)
    R(sh, '33R', 130, 88, 'LCD_SCK_MCU', 'LCD_SCK', horiz=True, L=2)
    R(sh, '33R', 130, 92, 'LCD_MOSI_MCU', 'LCD_MOSI', horiz=True, L=2)
    R(sh, '10k', 146, 92, '+3V3', 'LCD_MEMCS')
    R(sh, '10k', 150, 92, '+3V3', 'LCD_TSCS')
    R(sh, '10k', 154, 92, '+3V3', 'LCD_SDCS')
    R(sh, '0R', 130, 100, 'SPARE36', 'EYESPI_GP1', horiz=True, L=2, dnp=True)
    R(sh, '0R', 130, 104, 'SPARE37', 'EYESPI_GP2', horiz=True, L=2, dnp=True)
    C(sh, '10uF', 160, 92, '+3V3', 'GND', fp=C0805, extra=V25)
    C(sh, '100nF', 164, 92, '+3V3', 'GND', extra=V50)
    sh.notes(['Pin order from Adafruit EYESPI breakout (EYE_SPI_DISPLAY_BOTCONTACT): 1 VIN 2 LITE 3 GND 4 SCK',
              '5 MOSI 6 MISO 7 DC 8 RST 9 TCS 10 SDCS 11 MEMCS 12 TSCS 13 SCL 14 SDA 15 INT 16 BUSY 17 GP1 18 GP2.',
              'SCL/SDA = mux ch5 (4.7k on ports sheet). Unused selects 10k up. GP1/GP2 via DNP 0R from GPIO36/37.'],
             100, 115, C_UI)
    return sh

# =====================================================================================
# Sheet 5: I2C mux, I/O expander, 5 port eFuses + connectors
# =====================================================================================
def sheet_ports():
    sh = Sheet('I2C mux, expander, peripheral ports', 'ports.kicad_sch', page=5, size=(720, 460))
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
              'ch0-ch3 -> J1-J4 (E0001 rev C), ch4 -> J5 (E0002 rev B), ch5 -> EYESPI touch: 4.7k to 3V3.',
              'ch6/ch7 spare: 10k pull-ups. Firmware: <= 4 channels open, writes only.'], 2, 62, C_PORT)

    sh.rect(114, 0, 232, 70, C_PORT, 'SYSTEM I/O EXPANDER TCA9535 (I2C0 0x20)')
    sh.place('Interface_Expansion:TCA9535PWR', 'U9', 'TCA9535PWR', 150, 34, 0, refpos=(142, 12, 'left'),
             valpos=(142, 13, 'left'))
    sh.tie('U9', ['3', '2', '21'], 'GND')
    sh.nets('U9', {'21': 'GND', '2': 'GND', '3': 'GND', '12': 'GND', '24': '+3V3', '22': 'I2C0_SCL',
                   '23': 'I2C0_SDA', '1': 'EXP_INT_N', '4': 'PORT1_OFF', '5': 'PORT2_OFF', '6': 'PORT3_OFF',
                   '7': 'PORT4_OFF', '8': 'PORT5_OFF', '9': 'CHG_CE_N', '10': 'EXP_P06', '11': 'BAL_EN',
                   '13': 'PORT1_FLT_N', '14': 'PORT2_FLT_N', '15': 'PORT3_FLT_N', '16': 'PORT4_FLT_N',
                   '17': 'PORT5_FLT_N', '18': 'OV2_N', '19': 'EXP_P16', '20': 'EXP_P17'}, L=2)
    C(sh, '100nF', 120, 8, '+3V3', 'GND', extra=V50)
    for i in range(5):
        R(sh, '100k', 170 + 4 * i, 8, '+3V3', 'PORT%d_OFF' % (i + 1))
        R(sh, '10k', 170 + 4 * i, 20, '+3V3', 'PORT%d_FLT_N' % (i + 1))
    for i, nn in enumerate(('OV2_N', 'EXP_P06', 'EXP_P16', 'EXP_P17')):
        R(sh, '10k', 192 + 4 * i, 8, '+3V3', nn)
    sh.notes(['Reset state (all inputs): P00-P04 PORTn_OFF 100k up -> ports OFF; P05 CHG_CE_N 10k up (charger sheet)',
              '-> charging OFF; P07 BAL_EN pulled down at Q10 -> balancing OFF. P10-P15 inputs with 10k pull-ups.',
              'INT -> GPIO7. P06/P16/P17 spare (10k pull-ups).'], 116, 62, C_PORT)

    # ---- 5 ports
    for i in range(5):
        n = i + 1
        x0 = 2 + 46 * i
        big = (n == 5)
        sh.rect(x0 - 2, 72, x0 + 44, 156, C_PORT,
                'PORT %d: J%d %s' % (n, n, 'GH6 E0002 rev B, 2.0 A' if big else 'GH4 E0001 rev C, 0.87 A'))
        u = 'U%d' % (9 + n)
        sh.place('E0003:TPS259470L', u, 'TPS259470ARPW', x0 + 24, 98, 0, refpos=(x0 + 17, 89, 'left'),
                 valpos=(x0 + 17, 90, 'left'))
        P = 'PORT%d' % n
        sh.nets(u, {'5': 'VSYS', '6': 'PBUS_%d' % n, '1': P + '_EN', '2': P + '_OVLO', '7': P + '_DVDT',
                    '4': P + '_FLT_N', '3': None, '9': P + '_ILM', '10': P + '_ITIMER', '8': 'GND'}, L=2)
        divider(sh, '1M 1%', '232k 1%', x0 + 1, 78, 'VSYS', P + '_EN', 'GND')
        divider(sh, '1M 1%', '137k 1%', x0 + 12, 78, 'VSYS', P + '_OVLO', 'GND')
        fet(sh, 'Q%d' % (2 + n), x0 + 4, 108, P + '_OFF', P + '_EN', 'GND')
        C(sh, '1.8nF', x0 + 10, 116, P + '_DVDT', 'GND', extra=V50)
        C(sh, '22nF', x0 + 15, 116, P + '_ITIMER', 'GND', extra=V50)
        R(sh, '1.65k 1%' if big else '3.83k 1%', x0 + 20, 116, P + '_ILM', 'GND')
        C(sh, '100nF', x0 + 25, 116, 'VSYS', 'GND', extra=V50)
        dtv = nref('D')
        sh.place('Diode:SMF9V0A', dtv, 'SMF9.0A', x0 + 32, 108, 270, fp='Diode_SMD:D_SOD-123F',
                 refpos=(x0 + 33.5, 107.5, 'left'), valpos=(x0 + 33.5, 108.5, 'left'))
        sh.net(dtv, '1', 'PBUS_%d' % n)
        sh.net(dtv, '2', 'GND')
        # I2C: 220R series + ESD at the connector
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
                     valpos=(x0 + 38, 122, None), desc='E0002 rev B port: 1,2 PBUS 3 SCL 4 SDA 5,6 GND')
            sh.tie(j, ['5', '6'], 'GND')
            sh.tie(j, ['1', '2'], 'PBUS_5')
            sh.nets(j, {'1': 'PBUS_5', '2': 'PBUS_5', '3': P + '_SCL_C', '4': P + '_SDA_C', '5': 'GND', '6': 'GND',
                        'MP': 'GND'}, L=2)
        else:
            sh.place('Connector_Generic_MountingPin:Conn_01x04_MountingPin', j, 'SM04B-GHS-TB', x0 + 38, 128, 0,
                     fp='Connector_JST:JST_GH_SM04B-GHS-TB_1x04-1MP_P1.25mm_Horizontal', refpos=(x0 + 38, 122, None),
                     valpos=(x0 + 38, 123, None), desc='E0001 rev C port: 1 PBUS 2 SCL 3 SDA 4 GND')
            sh.nets(j, {'1': 'PBUS_%d' % n, '2': P + '_SCL_C', '3': P + '_SDA_C', '4': 'GND', 'MP': 'GND'}, L=2)
        sh.notes(['Silkscreen: "PBUS 6-9 V" + "%d" + "%s"' % (n, 'E0002' if big else 'E0001'),
                  'I_LIM %s; OVLO 9.96/9.05 V; UVLO 6.37/5.79 V' % ('2.03 A (1.80-2.20)' if big else '0.87 A (0.74-1.00)')],
                 x0, 151, C_PORT)
    sh.rect(234, 72, 262, 156, C_PORT, 'PBUS BULK')
    C(sh, '47uF', 240, 90, 'VSYS', 'GND', fp=C1210, extra=V16)
    C(sh, '47uF', 246, 90, 'VSYS', 'GND', fp=C1210, extra=V16)
    sh.notes(['2 x 47 uF/16 V on VSYS', 'next to the eFuse group.'], 236, 100, C_PORT)
    return sh


# ------------------------------------------------------------------ purchasing fields
import csv
MPN_BY_REF = {'U1': 'ESP32-S3-WROOM-1-N16R2', 'U2': 'BQ25798RQMR', 'U3': 'STUSB4500QTR', 'U4': 'USBLC6-2SC6',
              'U5': 'TPS629210DRLR', 'U6': 'S-8252AAG-M6T1U', 'U7': 'BQ29209DRBR', 'U8': 'PCA9548APW,118',
              'U9': 'TCA9535PWR', 'U15': 'MAX17205G+T', 'J10': 'FH12-18S-0.5SH(55)', 'J11': 'USB4105-GF-A',
              'L1': 'SRP7028A-2R2M', 'L3': 'DFE252012PD-2R2M=P2', 'F1': '0452010.MRL', 'Q1': 'PSMN2R0-30YLDX',
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
PN_FALLBACK = {'GRM155R71H473KE14D': ('Murata Electronics', 'DigiKey', '490-10702-1-ND'),
               'SM06B-GHS-TB(LF)(SN)': ('JST Sales America Inc.', 'DigiKey', '455-1568-1-ND'),
               'TPS259470ARPWR': ('Texas Instruments', 'DigiKey', '296-TPS259470ARPWRCT-ND')}
NEW_MFR = {'RC04': 'YAGEO', 'GRM1': 'Murata Electronics', 'BAT5': 'Diodes Incorporated'}


def assign_fields(sheets):
    """Add MPN / Manufacturer / Supplier / Supplier PN from bom/E0003_digikey_bom.csv; report gaps."""
    from sch_core import prop as _prop
    rows = {r['MPN']: r for r in csv.DictReader(open(os.path.join(PROJ, 'bom', 'E0003_digikey_bom.csv')))}
    fab_bom = os.path.join(PROJ, 'fab', 'E0003_revA', 'E0003_revA_BOM.csv')   # Parts' released BOM wins
    if os.path.exists(fab_bom):
        rows.update({r['MPN']: r for r in csv.DictReader(open(fab_bom)) if r.get('MPN')})
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
    write_all(PROJ, 'E0003 ESP32 control box mainboard', 'A', '2026-10-11',
              ['2S Molicel P50B, BQ25798 + STUSB4500, MAX17205 stack-only, 5 x TPS259470A ports',
               'Spec docs/SPEC.md v1.2; generated by build/scripts/gen_sch.py'], sheets)
    n = sum(len([s for s in sh.symbols if not str(s[1][1]).startswith('power:')]) for sh in sheets)
    print('wrote', len(sheets), 'sheets,', n, 'symbols')


if __name__ == '__main__':
    main()
