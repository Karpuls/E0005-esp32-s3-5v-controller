#!/bin/sh
# drc.sh : DRC of the saved board, all severities + parity; prints counts and courtyard/clearance pairs
cd "$(dirname "$0")/../../.."
K="/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/bin/kicad-cli"
"$K" pcb drc --schematic-parity --severity-all -o build/layout/drc.rpt E0005_controller.kicad_pcb >/dev/null 2>&1
grep -oE "^\[[a-z_]+\]" build/layout/drc.rpt | sort | uniq -c
python3 - <<'PY'
import re
t=open('build/layout/drc.rpt').read().split('\n[')
for b in t:
    k=b.split(']')[0]
    if k in ('courtyards_overlap','clearance','shorting_items','solder_mask_bridge','copper_edge_clearance','silk_edge_clearance','hole_clearance','npth_inside_courtyard','pth_inside_courtyard','malformed_courtyard','missing_courtyard','footprint_type_mismatch','extra_footprint','missing_footprint','net_conflict','lib_footprint_mismatch','holes_co_located','drill_out_of_range','annular_width','hole_to_hole','invalid_outline','items_not_allowed','text_height','text_thickness'):
        refs=re.findall(r'(?:Footprint|of|Pad \S+ \[[^\]]*\] of|on) ([A-Z]+[0-9]+)',b)
        print(k, ' '.join(dict.fromkeys(refs)) or b.split('\n')[1:3])
PY
