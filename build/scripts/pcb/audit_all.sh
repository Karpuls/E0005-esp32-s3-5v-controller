#!/bin/sh
# audit_all.sh : placement_audit + route_check for every IC -> build/layout/audit/
cd "$(dirname "$0")/../../.."
export KICAD_API_SOCKET=${KICAD_API_SOCKET:-ipc:///tmp/e5ipc/api.sock}
R="--track 0.2 --clear 0.15 --via 0.6 --edge 0.3"; S=~/.claude/skills/layout-placement/scripts/run.sh; B="$PWD/E0005_controller.kicad_pcb"
mkdir -p build/layout/audit
for u in ${*:-U1 U2 U4 U5 U6 U8 U9 U10 U11 U12 U13 U14 U15 U16 U17}; do
  $S placement_audit.py "$B" --ic $u $R > build/layout/audit/audit_$u.txt 2>&1
  timeout 900 $S route_check.py "$B" --ic $u $R > build/layout/audit/route_$u.txt 2>&1 || echo "route_check $u exit $?" >> build/layout/audit/route_$u.txt
  echo "done $u"
done
