#!/bin/sh
# lay.sh tag layer x0 y0 x1 y1 [dpi] : PNG of one copper layer (+F.Fab/Edge) of the saved board, cropped (board-local mm)
cd "$(dirname "$0")/../.."
K="/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/bin/kicad-cli"
o=build/route/png/$1; rm -rf "$o"; mkdir -p "$o"
case $2 in B.Cu) extra="--mirror"; fab=B.Fab;; *) extra=""; fab=F.Fab;; esac
"$K" pcb export png -o "$o" -l $2 --cl $fab,Edge.Cuts --dpi ${7:-400} --bg-color $extra --sp E0005_controller.kicad_pcb >/dev/null 2>&1
f=$(ls "$o"/*.png | head -1)
~/.local/bin/uv run -q --with pillow python build/scripts/pcb/crop.py "$f" "$o.png" $3 $4 $5 $6
echo "$o.png"
