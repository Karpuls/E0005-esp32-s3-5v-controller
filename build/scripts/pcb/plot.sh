#!/bin/sh
# plot.sh <tag> : PNG of the saved canonical board (top: F.Fab+F.CrtYd+F.Cu+Edge; bottom mirrored)
K="/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/bin/kicad-cli"
cd "$(dirname "$0")/../../.."
o=build/layout/png/$1; rm -rf "$o"; mkdir -p "$o"
"$K" pcb export png -o "$o/top" -l F.Fab --cl F.Cu,F.CrtYd,Edge.Cuts,Dwgs.User,Cmts.User,F.SilkS --dpi ${DPI:-250} --bg-color --sp E0005_controller.kicad_pcb >/dev/null 2>&1
"$K" pcb export png -o "$o/bot" -l B.Fab --cl B.Cu,B.CrtYd,Edge.Cuts,B.SilkS --dpi ${DPI:-250} --bg-color --sp --mirror E0005_controller.kicad_pcb >/dev/null 2>&1
ls "$o"/*/*
for f in top bot; do ~/.local/bin/uv run -q --with pillow python build/scripts/pcb/crop.py "$o/$f/E0005_controller-$( [ $f = top ] && echo F || echo B )_Fab.png" "$o/$f.png" $2 $3 $4 $5; done
