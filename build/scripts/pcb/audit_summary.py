# audit_summary.py : per IC, route_check failures that involve the IC itself, plus audit fronts / no-via-site
import glob, os, re
for f in sorted(glob.glob('build/layout/audit/route_U*.txt'), key=lambda s: int(re.findall(r'U(\d+)', s)[0])):
    u = re.findall(r'(U\d+)', f)[0]
    t = open(f).read()
    tot = re.findall(r'local links routed in both orders: (\d+)/(\d+)', t)
    own = [l.strip() for l in t.splitlines() if 'FAILED' in l and re.search(r'\b%s\.' % u, l)]
    both = [l for l in own if 'both orders' in l]
    esc = re.findall(r'escapes to the edge routed in both orders: (\S+)', t)
    a = open(f.replace('route_', 'audit_')).read() if os.path.exists(f.replace('route_', 'audit_')) else ''
    fronts = a.split('fronts')[1].strip().splitlines()[1:] if 'fronts' in a else []
    print('%-4s all-part links %s | own-pin links failing: %d (both orders: %d) | escapes %s | blocked fronts %d' % (
        u, '/'.join(tot[0]) if tot else '?', len(own), len(both), esc[0] if esc else ('timeout' if 'exit' in t else '?'), len(fronts)))
    for l in both:
        print('      ', re.sub(r'/[^/()]*/', '', l))
