#!/usr/bin/env python3
"""bom/E0005_digikey_bom.csv from the schematic (E0003 column format). Never edit the CSV by hand.

Stock/price data: E0003's API-checked BOM (bom/E0003_digikey_bom.csv + fab BOM, 2026-10-18) for reused MPNs,
bom/new_parts_digikey.csv (pcbparts digikey_get_part, 2026-10-27) for new ones. No BOM-wide API sweep.
"""
import os, sys, csv, re, glob, collections
sys.path.insert(0, os.path.dirname(__file__))
from sexp import parse, find, findall
PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
E3 = '/home/karpulis/KiCad/E0003 - ESP32 control box mainboard'
F = ['Supplier', 'Qty', 'QtyBasis', 'References', 'Value', 'Footprint', 'MPN', 'Manufacturer', 'SupplierPN', 'Stock',
     'Lifecycle', 'UnitEUR', 'LeadWeeks', 'DNP', 'OwnerStock', 'Notes']
old = {}
for f in (os.path.join(E3, 'bom', 'E0003_digikey_bom.csv'), os.path.join(E3, 'fab', 'E0003_revA', 'E0003_revA_BOM.csv')):
    for r in csv.DictReader(open(f)):
        if r.get('MPN') and r.get('Stock'):
            old[r['MPN']] = r
new = {r['MPN']: r for r in csv.DictReader(open(os.path.join(PROJ, 'bom', 'new_parts_digikey.csv')))}
common = {r['MPN']: r for r in csv.DictReader(open(os.path.join(E3, 'bom', 'common_parts_across_projects.csv')))}
g = collections.OrderedDict()
for f in sorted(glob.glob(os.path.join(PROJ, '*.kicad_sch'))):
    for s in findall(parse(open(f).read()), 'symbol'):
        if find(s, 'lib_id') is None or find(s, 'lib_id')[1].startswith('power:') or find(s, 'in_bom')[1] != 'yes':
            continue
        pr = {p[1]: p[2] for p in findall(s, 'property')}
        k = (pr['Value'], pr['Footprint'].split(':')[-1], pr.get('MPN', ''), pr.get('Manufacturer', ''),
             pr.get('Supplier PN', ''), find(s, 'dnp')[1] == 'yes')
        g.setdefault(k, []).append(pr['Reference'])
key = lambda r: (re.sub(r'\d', '', r), int(re.sub(r'\D', '', r) or 0))
rows, issues = [], []
for (val, fp, mpn, mfr, spn, dnp), refs in sorted(g.items(), key=lambda kv: key(sorted(kv[1], key=key)[0])):
    refs.sort(key=key)
    row = dict(Qty=len(refs), QtyBasis='schematic', References=' '.join(refs), Value=val, Footprint=fp, MPN=mpn,
               Manufacturer=mfr, SupplierPN=spn, DNP='DNP' if dnp else '', OwnerStock='no', Notes='')
    if mpn in new:
        n = new[mpn]
        row.update(Supplier='DigiKey', SupplierPN=n['SupplierPN'], Stock=n['Stock'], Lifecycle=n['Lifecycle'],
                   UnitEUR='%s USD @1' % n['UnitUSD'], Notes='NEW in E0005, DigiKey checked %s. %s' % (n['Checked'], n['Note']))
    elif mpn in old:
        o = old[mpn]
        row.update(Supplier=o.get('Supplier', 'DigiKey'), SupplierPN=o.get('SupplierPN') or spn, Stock=o.get('Stock', ''),
                   Lifecycle=o.get('Lifecycle', ''), UnitEUR=o.get('UnitEUR', ''), LeadWeeks=o.get('LeadWeeks', ''),
                   OwnerStock=o.get('OwnerStock', 'no'), Notes=('E0003 data 2026-10-18. ' + o.get('Notes', '')).strip())
        if o.get('Supplier') == 'LCSC':
            row['Notes'] += ' BOM EXCEPTION (not DigiKey)'
    elif mpn in common:
        c = common[mpn]
        row.update(Supplier=c['Supplier'], SupplierPN=c['SupplierPN'] or spn,
                   Notes='Common part (%s); stock not re-queried (E0001/E0002 BOMs)' % c['Projects'])
    else:
        row.update(Supplier='?', Notes='NO SUPPLIER DATA')
        issues.append(mpn or val)
    rows.append(row)
for r in csv.DictReader(open(os.path.join(E3, 'bom', 'E0003_digikey_bom.csv'))):   # off-board lines, as E0003
    if 'off-board' in r['References'].lower() or r['MPN'] == 'INR21700-P50B':
        rows.append({k: r.get(k, '') for k in F})
with open(os.path.join(PROJ, 'bom', 'E0005_digikey_bom.csv'), 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=F)
    w.writeheader()
    w.writerows(rows)
onb = sum(int(r['Qty']) for r in rows if r['QtyBasis'] == 'schematic')
print(len(rows), 'lines,', onb, 'on-board parts; issues:', issues)
for r in rows:
    st = str(r.get('Stock', '')).split()[0] if r.get('Stock') else ''
    if r['Supplier'] != 'DigiKey' or (st.isdigit() and int(st) < 10 * int(r['Qty'])):
        print('  EXCEPTION/LOW:', r['Supplier'], r['MPN'], r['Stock'], 'qty', r['Qty'], r['Notes'][:90])
