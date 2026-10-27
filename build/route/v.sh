#!/bin/sh
# v.sh x0 y0 x1 y1 name [layers]
cd "$(dirname "$0")"; python3 build.py >/dev/null && ~/.local/bin/uv run -q --with matplotlib --with numpy python view.py "$@" 2>&1 | tail -1
