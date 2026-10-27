"""Create the initial E0005_controller.kicad_pcb from the schematic netlist (one-off, phase 3 step 1).

- every schematic component with its library footprint and nets (from build/layout/current.net)
- E0003's layer table, stackup (JLC04161H-3313) and board setup, copied verbatim
- the E0003 outline (4 x M3) and the holders BH1/BH2 at E0003's positions (locked, bottom)
- parts that E0003 has with the same reference and footprint start at E0003's position;
  every other part is parked in a grid below the board for the placement scripts to move.

Usage: python3 pcb_create.py [out.kicad_pcb]
After this the board is edited only through KiCad IPC (layout-placement scripts).
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
import pcb_kpcb as kpcb
from pcb_kpcb import OX, OY
from pcb_sexp import parse, dump

E3 = '/home/karpulis/KiCad/E0003 - ESP32 control box mainboard/E0003_control_box.kicad_pcb'
OUTLINE = 'E0005_mech:E0003_Outline_125x65_4xM3'
# power-stage parts that are new in E0005 (start in the staging grid, not at E0003's spot)
NEW_POWER = {'U2', 'L1', 'L2', 'C2', 'C8', 'C9', 'C11', 'C18', 'C20', 'C1'}


def fpname(libid):
    return libid.split(':')[1]


def e3_positions():
    t = parse(open(E3).read())
    pos = {}
    for fp in [x for x in t if isinstance(x, list) and x and x[0] == 'footprint']:
        ref = [p[2] for p in fp if isinstance(p, list) and p[0] == 'property' and p[1] == 'Reference'][0]
        at = [p for p in fp if isinstance(p, list) and p[0] == 'at'][0]
        lay = [p for p in fp if isinstance(p, list) and p[0] == 'layer'][0][1]
        pos[ref] = (fpname(fp[1]), float(at[1]) - OX, float(at[2]) - OY,
                    float(at[3]) if len(at) > 3 else 0.0, 'B' if lay == 'B.Cu' else 'F')
    hdr = {}
    for key in ('layers', 'setup'):
        blk = [x for x in t if isinstance(x, list) and x and x[0] == key][0]
        hdr[key] = blk
    return pos, hdr


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else kpcb.BOARD
    comps, nets = kpcb.load_netlist(os.path.join(kpcb.PROJ, 'build', 'layout', 'current.net'))
    e3, hdr = e3_positions()
    parts = {}
    staged = []
    for ref in sorted(comps, key=lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))):
        c = comps[ref]
        p = e3.get(ref)
        if p and p[0] == fpname(c['footprint']) and ref not in NEW_POWER:
            parts[ref] = kpcb.Part(ref, c, p[1], p[2], p[3], p[4], nets)
            if ref == 'U1':      # WROOM-1 EP pad-vias are 0.2 mm drills (< JLC 0.3): board vias at routing
                parts[ref].drop_pads.append(lambda pad: str(pad[2]) == 'thru_hole' and pad[1] == '41')
            if ref in ('BH1', 'BH2'):
                parts[ref].locked = True
        else:
            staged.append(ref)
    # staging grid below the board (y > 40 mm from the centre), 7 mm pitch, big parts on their own
    x0, y0, col = -60.0, 42.0, 0
    for ref in staged:
        c = comps[ref]
        big = any(k in c['footprint'] for k in ('IHLP', '1121', '2512', 'LFPAK', 'QFN', 'RGE'))
        pitch = 12.0 if big else 6.0
        parts[ref] = kpcb.Part(ref, c, x0, y0, 0.0, 'F', nets)
        x0 += pitch
        if x0 > 60:
            x0, y0 = -60.0, y0 + 8.0
    oc = dict(ref='OUT1', value='E0003_Outline_125x65_4xM3', footprint=OUTLINE, tstamp='', fields=[],
              props={'exclude_from_bom': '', 'exclude_from_pos_files': ''}, board_only=True)
    o = kpcb.Part('OUT1', oc, 0.0, 0.0, 0, 'F', {})
    o.locked = True
    o.ref_silk = None
    parts['OUT1'] = o

    items = [parts[r].build() for r in sorted(parts, key=lambda r: (r[0], len(r), r))]
    txt = ['(kicad_pcb\n\t(version 20260206)\n\t(generator "e0005_gen_pcb")\n\t(generator_version "10.99")\n'
           '\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper "A4")\n',
           '\t(title_block\n\t\t(title "E0005 ESP32-S3 5V controller")\n\t\t(date "2026-10-27")\n\t\t(rev "A")\n'
           '\t\t(comment 1 "4 layers 1.6 mm, JLC04161H-3313, 1 oz outer / 0.5 oz inner")\n\t)\n']
    txt.append('\t' + dump(hdr['layers'], 1) + '\n')
    txt.append('\t' + dump(hdr['setup'], 1) + '\n')
    for it in items:
        txt.append('\t' + dump(it, 1) + '\n')
    txt.append(')\n')
    open(out, 'w').write(''.join(txt))
    print('wrote', out, len(items), 'footprints;', len(staged), 'staged:', ' '.join(staged))


if __name__ == '__main__':
    main()
