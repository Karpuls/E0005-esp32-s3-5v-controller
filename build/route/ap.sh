#!/bin/sh
# ap.sh : build items, apply to the canonical board over IPC, DRC
cd "$(dirname "$0")"
python3 build.py >/dev/null || exit 1
KICAD_API_SOCKET=ipc:///tmp/e5ipc/api.sock ~/.cache/kistack/layout-placement/a761496662742274/bin/python apply.py items.json || exit 1
./drc.sh
