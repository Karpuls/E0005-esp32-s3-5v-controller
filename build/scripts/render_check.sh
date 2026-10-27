#!/bin/bash
# ERC + netlist + PDF + connectivity report for the E0005 schematic
set -e
cd "$(dirname "$0")/../.."
K=/home/karpulis/.backplane-bend/kicad/10.99.0-bp.4/bin/kicad-cli
mkdir -p build/out
"$K" sch erc --severity-all -o build/out/erc.rpt E0005_controller.kicad_sch | tail -1
grep -E "ERC messages" build/out/erc.rpt
"$K" sch export netlist --format kicadsexpr -o build/out/E0005.net E0005_controller.kicad_sch >/dev/null
"$K" sch export pdf -o build/out/E0005_sch.pdf E0005_controller.kicad_sch >/dev/null
python3 - <<'PY'
import sys
sys.path.insert(0, 'build/scripts')
from sexp import parse, find, findall
n = parse(open('build/out/E0005.net').read())
for net in findall(find(n, 'nets'), 'net'):
    nm = find(net, 'name')[1]
    nodes = ['%s.%s' % (find(x, 'ref')[1], find(x, 'pin')[1]) for x in findall(net, 'node')]
    if (nm.startswith('Net-(') or len(nodes) < 2) and not nm.startswith('unconnected-'):
        print('  check net:', nm, nodes)
PY
