#!/usr/bin/env bash
# E0005 rev A fabrication package -> fab/E0005_revA/ (kicad-export skill).
# Deterministic: reads only committed project files; re-running gives the same output apart from timestamps.
# Usage: build/scripts/fab_export.sh            (exit 1 if DRC/ERC are not at the accepted state)
set -euo pipefail

K=${KICAD_CLI:-/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/bin/kicad-cli}
PROJ=$(cd "$(dirname "$0")/../.." && pwd)
NAME=E0005_controller
REV=E0005_revA
PCB="$PROJ/$NAME.kicad_pcb"
SCH="$PROJ/$NAME.kicad_sch"
OUT="$PROJ/fab/$REV"
CONVERT_POS=${CONVERT_POS:-$HOME/.claude/skills/kicad-export/scripts/convert_position.py}
LAYERS=F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts

cd "$PROJ"
"$K" version
rm -rf "$OUT/gerbers" "$OUT/assembly" "$OUT/reports" "$OUT/3d" "$OUT/${REV}_gerbers_JLC.zip"
mkdir -p "$OUT/gerbers" "$OUT/assembly" "$OUT/reports" "$OUT/3d" "$OUT/docs/gerber_review"

# ---- 1. ERC / DRC ---------------------------------------------------------------------------------
"$K" sch erc --output "$OUT/reports/${REV}_ERC.rpt" --format report --units mm --severity-all "$SCH"
"$K" sch erc --output "$OUT/reports/${REV}_ERC.json" --format json --units mm --severity-all "$SCH"
"$K" pcb drc --output "$OUT/reports/${REV}_DRC.rpt" --format report --units mm --severity-all \
    --schematic-parity --refill-zones "$PCB"
"$K" pcb drc --output "$OUT/reports/${REV}_DRC.json" --format json --units mm --severity-all \
    --schematic-parity --refill-zones "$PCB"

# Gate: ERC 0 errors; DRC 0 errors, 0 unconnected, 0 parity, the only violation U1 lib_footprint_mismatch.
python3 - "$OUT/reports/${REV}_DRC.json" "$OUT/reports/${REV}_ERC.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); e = json.load(open(sys.argv[2]))
viol = d.get('violations', [])
unc = d.get('unconnected_items', []); par = d.get('schematic_parity', [])
other = [v for v in viol if not (v['type'] == 'lib_footprint_mismatch'
         and any('U1' in i.get('description', '') for i in v.get('items', [])))]
erc = [v for s in e.get('sheets', []) for v in s.get('violations', [])]
erc_err = [v for v in erc if v.get('severity') == 'error']
print(f"DRC: {len(viol)} violations ({len(viol)-len(other)} = U1 lib_footprint_mismatch), "
      f"{len(unc)} unconnected, {len(par)} parity | ERC: {len(erc)} violations, {len(erc_err)} errors")
if other or unc or par or erc_err:
    for v in other[:20]: print('  DRC:', v['severity'], v['type'], v['description'])
    for v in erc_err[:20]: print('  ERC:', v['type'], v['description'])
    print('FAILURE: DRC/ERC not at the accepted state; fab export stopped.'); sys.exit(1)
EOF

# ---- 2. Gerbers + Excellon drill (JLC KiCad settings) --------------------------------------------
# Protel extensions, no X2 (JLC's KiCad guide), soldermask subtracted from silk, zones refilled before plotting.
# Vias are tented by the board setting (setup: tenting front/back yes), so the masks have no via openings.
"$K" pcb export gerbers --output "$OUT/gerbers/" --layers "$LAYERS" --no-x2 --subtract-soldermask \
    --precision 6 --check-zones "$PCB"
"$K" pcb export drill --output "$OUT/gerbers/" --format excellon --drill-origin absolute \
    --excellon-units mm --excellon-zeros-format decimal --excellon-oval-format alternate \
    --excellon-separate-th --generate-map --map-format gerberx2 "$PCB"
mv "$OUT"/gerbers/*-drl_map.gbr "$OUT/reports/"
"$K" pcb export drill --output "$OUT/reports/" --format excellon --drill-origin absolute \
    --excellon-units mm --excellon-separate-th --generate-report \
    --report-path "$OUT/reports/${REV}_drill_report.txt" "$PCB" >/dev/null
rm -f "$OUT"/reports/*.drl
(cd "$OUT/gerbers" && LC_ALL=C ls | sort | TZ=UTC zip -X -q -D "../${REV}_gerbers_JLC.zip" -@)

# ---- 3. Placement (KiCad + JLC CPL) --------------------------------------------------------------
for side in front back both; do
    tag=$side; [ "$side" = both ] && tag=all
    "$K" pcb export pos --output "$OUT/assembly/${REV}_pos_${tag}.csv" --format csv --units mm --side "$side" "$PCB"
done
"$K" pcb export pos --output "$OUT/assembly/.pos_fitted.csv" --format csv --units mm --side both --exclude-dnp "$PCB"
python3 "$CONVERT_POS" "$OUT/assembly/.pos_fitted.csv" "$OUT/assembly/${REV}_CPL_JLC.csv"
# JLC's CPL template spells the layer out: T/B -> Top/Bottom (PlaceRoute, fab review 2026-10-28)
python3 -I - "$OUT/assembly/${REV}_CPL_JLC.csv" <<'EOF'
import csv, sys
p = sys.argv[1]
rows = list(csv.reader(open(p, newline='')))
i = rows[0].index('Layer')
for r in rows[1:]:
    r[i] = {'T': 'Top', 'B': 'Bottom', 'top': 'Top', 'bottom': 'Bottom'}.get(r[i], r[i])
csv.writer(open(p, 'w', newline=''), lineterminator='\r\n').writerows(rows)
EOF
rm -f "$OUT/assembly/.pos_fitted.csv"

# ---- 4. BOM (DigiKey primary, JLC format secondary) + DNP list -----------------------------------
python3 build/scripts/make_bom.py
cp bom/E0005_digikey_bom.csv "$OUT/${REV}_BOM.csv"
python3 - "$OUT" "$REV" <<'EOF'
import csv, sys, os, re
out, rev = sys.argv[1:]
rows = list(csv.DictReader(open(os.path.join(out, rev + '_BOM.csv'))))
onb = [r for r in rows if r['QtyBasis'] == 'schematic']
with open(os.path.join(out, 'assembly', rev + '_BOM_JLC.csv'), 'w', newline='') as fh:
    w = csv.writer(fh)
    w.writerow(['Comment', 'Designator', 'Footprint', 'Manufacturer', 'Manufacturer Part', 'LCSC Part #'])
    for r in onb:
        if r['DNP']:
            continue
        refs = r['References'].split()
        w.writerow([r['Value'], ','.join(refs), r['Footprint'], r['Manufacturer'], r['MPN'],
                    (re.search(r'C\d+', r['SupplierPN']) or [''])[0] if r['Supplier'] == 'LCSC' else ''])
dnp = sorted(ref for r in onb if r['DNP'] for ref in r['References'].split())
open(os.path.join(out, 'assembly', rev + '_DNP.txt'), 'w').write(
    '# DNP parts (not fitted, excluded from the JLC CPL and BOM)\n' + ''.join(d + '\n' for d in dnp))
EOF

# ---- 5. Assembly drawings, schematic PDF, STEP ---------------------------------------------------
"$K" pcb export pdf --output "$OUT/assembly/${REV}_assembly_top.pdf" --mode-single \
    --layers F.Fab,F.CrtYd,Edge.Cuts --include-border-title --black-and-white --exclude-value \
    --crossout-DNP-footprints-on-fab-layers --sketch-pads-on-fab-layers --drill-shape-opt 0 "$PCB"
"$K" pcb export pdf --output "$OUT/assembly/${REV}_assembly_bottom.pdf" --mode-single --mirror \
    --layers B.Fab,B.CrtYd,Edge.Cuts --include-border-title --black-and-white --exclude-value \
    --crossout-DNP-footprints-on-fab-layers --sketch-pads-on-fab-layers --drill-shape-opt 0 "$PCB"
"$K" sch export pdf --output "$OUT/docs/${REV}_schematic.pdf" "$SCH"
"$K" pcb export step --output "$OUT/3d/${REV}.step" --force --subst-models --no-dnp "$PCB"

# ---- 6. Gerber review renders (kicad-gerbers skill; needs pygerber, see gerber_review.py) -------------
PYG=${PYGERBER_PY:-/tmp/e5gv/.venv/bin/python}
if [ -x "$PYG" ]; then
    "$PYG" -I build/scripts/gerber_review.py > "$OUT/docs/gerber_review/gerber_review.log"
else
    echo "NOTE: pygerber venv not found ($PYG); gerber review renders not refreshed"
fi

echo "fab package written to $OUT"
