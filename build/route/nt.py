"""nt.py NET... : list the tracks/vias of the given nets (new frame) from items.json"""
import json, sys
for it in json.load(open('items.json')):
    n = it['net'].split('/')[-1]
    if n in sys.argv[1:]:
        print(n, it['k'], it.get('L', ''), it.get('a', it.get('p')), it.get('b', ''), it.get('w', it.get('d')))
