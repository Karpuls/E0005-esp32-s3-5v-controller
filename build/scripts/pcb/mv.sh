#!/bin/sh
# mv.sh [--save] REF=x,y,rot[,F|B] ... : board-local mm (centre 150,100) -> move.py (absolute)
cd "$(dirname "$0")/../../.."
export KICAD_API_SOCKET=${KICAD_API_SOCKET:-ipc:///tmp/e5ipc/api.sock}
args=""
for a in "$@"; do
  case $a in
    --*) args="$args $a";;
    *=*) r=${a%%=*}; v=${a#*=}; x=${v%%,*}; rest=${v#*,}; y=${rest%%,*}; tail=${rest#*,}
         [ "$tail" = "$rest" ] && tail=0
         X=$(python3 -c "print(round($x+150,4))"); Y=$(python3 -c "print(round($y+100,4))")
         args="$args $r=$X,$Y,$tail";;
  esac
done
exec ~/.claude/skills/layout-placement/scripts/run.sh move.py "$PWD/E0005_controller.kicad_pcb" $args 2>&1 | grep -v "no courtyard read for NT1"
