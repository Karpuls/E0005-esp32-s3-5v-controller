#!/bin/sh
# strict.sh : DRC on a copy with 0.15 mm copper clearance (house target), prints clearance-type violations
cd "$(dirname "$0")/../.."
d=/tmp/e5strict; rm -rf $d; mkdir -p $d
cp E0005_controller.kicad_pcb E0005_controller.kicad_pro $d/
sed 's/(rule "JLC clearance" (constraint clearance (min 0.09mm)))/(rule "JLC clearance" (constraint clearance (min 0.15mm)))/' E0005_controller.kicad_dru > $d/E0005_controller.kicad_dru
/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/bin/kicad-cli pcb drc --severity-all --refill-zones -o $d/drc.rpt $d/E0005_controller.kicad_pcb >/dev/null 2>&1
cp $d/drc.rpt build/route/strict.rpt
cd build/route; cp drc.rpt drc_main.rpt; cp strict.rpt drc.rpt; python3 dv.py clearance shorting_items hole_clearance; cp drc_main.rpt drc.rpt
