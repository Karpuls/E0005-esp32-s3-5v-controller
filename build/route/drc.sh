#!/bin/sh
# drc.sh : DRC (all severities, parity) of the canonical board -> drc.rpt; summary of non-unconnected violations
cd "$(dirname "$0")/../.."
K="/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/bin/kicad-cli"
"$K" pcb drc --schematic-parity --severity-all ${REFILL:+--refill-zones} -o build/route/drc.rpt E0005_controller.kicad_pcb 2>&1 | grep -i "found\|error" 
grep -oE "^\[[a-z_]+\]" build/route/drc.rpt | sort | uniq -c
