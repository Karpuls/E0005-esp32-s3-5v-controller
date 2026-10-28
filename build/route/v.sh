#!/bin/sh
# v.sh x0 y0 x1 y1 name [layers]
cd "$(dirname "$0")"; /home/karpulis/.cache/kistack/layout-placement/a761496662742274/bin/python build.py >/dev/null && ~/.local/bin/uv run -q --with matplotlib --with numpy python view.py "$@" 2>&1 | tail -1
