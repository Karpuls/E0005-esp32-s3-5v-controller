# e3dump.py x0 y0 x1 y1 out.json : E0003 tracks/vias/zones (board-local) in a window
import re, sys, json
E3 = "/home/karpulis/KiCad/E0003 - ESP32 control box mainboard/E0003_control_box.kicad_pcb"
t = open(E3).read()
x0, y0, x1, y1 = map(float, sys.argv[1:5])
nets = dict(re.findall(r'\n\t\(net (\d+) "([^"]*)"\)', t))
def nn(s):
    m = re.search(r'\(net (\d+)\)', s) or re.search(r'\(net "([^"]*)"\)', s)
    if not m: return ''
    return nets.get(m.group(1), m.group(1))
out = []
for m in re.finditer(r'\n\t\(segment\b(.*?)\n\t\)', t, re.S):
    s = m.group(1)
    a = re.search(r'\(start ([-\d.]+) ([-\d.]+)\)', s); b = re.search(r'\(end ([-\d.]+) ([-\d.]+)\)', s)
    w = float(re.search(r'\(width ([\d.]+)\)', s).group(1)); L = re.search(r'\(layer "([^"]+)"\)', s).group(1)
    A = (float(a.group(1)) - 150, float(a.group(2)) - 100); Bp = (float(b.group(1)) - 150, float(b.group(2)) - 100)
    if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 for p in (A, Bp)):
        out.append(dict(k='t', net=nn(s), w=w, L=L, a=A, b=Bp))
for m in re.finditer(r'\n\t\(via\b(.*?)\n\t\)', t, re.S):
    s = m.group(1); a = re.search(r'\(at ([-\d.]+) ([-\d.]+)\)', s)
    P = (float(a.group(1)) - 150, float(a.group(2)) - 100)
    if x0 <= P[0] <= x1 and y0 <= P[1] <= y1:
        out.append(dict(k='v', net=nn(s), p=P, d=float(re.search(r'\(size ([\d.]+)\)', s).group(1)), dr=0.3))
json.dump(out, open(sys.argv[5], 'w')); print(len(out), 'items')
