import importlib, importlib.util, sys, rt
MODS = [m for m in ['r_buck', 'r_chg', 'r_uin', 'r_bat', 'r_ports', 'r_mux', 'r_long', 'r_mcu', 'r_usb', 'r_lcd', 'r_south', 'r_cc', 'r_band', 'r_bundle', 'r_misc', 'r_ui', 'r_gnd', 'r_fix', 'r_planes'] if importlib.util.find_spec(m)]
for m in MODS:
    rt.NEWFRAME = False
    importlib.import_module(m)
import chamfer
pa, pleft = chamfer.padangle2()
print('pad exits squared', pa, 'left', len(pleft), pleft[:20])
nch, bad = chamfer.run()
print('chamfered', nch, 'left', len(bad), bad[:20])
print(rt.save(), len(rt.ITEMS))
