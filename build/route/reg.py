# reg.py x0 y0 x1 y1 : pads in window
import sys, rt
x0,y0,x1,y1 = map(float, sys.argv[1:5])
for k,p in sorted(rt.PADS.items(), key=lambda kv:(kv[1]['y'],kv[1]['x'])):
    if x0<=p['x']<=x1 and y0<=p['y']<=y1:
        b=p['bb']; print('%-9s %-18s %7.2f %7.2f  [%.2f %.2f %.2f %.2f]'%(k,(p['net'] or '-').split('/')[-1][:18],p['x'],p['y'],*b))
