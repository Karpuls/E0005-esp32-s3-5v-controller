# lp.py REF... : pad table (pin, net, x, y, size)
import sys, rt
for r in sys.argv[1:]:
    f = rt.FP[r]; print('%s %s @%.2f,%.2f r%.0f %s' % (r, f['val'], f['x'], f['y'], f['rot'], f['side']))
    for p in f['pads']:
        b = p['bb']; print('   %-3s %-22s %7.2f %7.2f  %.2fx%.2f' % (p['n'], (p['net'] or '-').split('/')[-1][:22], p['x'], p['y'], b[2]-b[0], b[3]-b[1]))
