import importlib, importlib.util, sys, rt
MODS = [m for m in ['r_buck', 'r_chg', 'r_uin', 'r_bat', 'r_ports', 'r_mux', 'r_long', 'r_mcu', 'r_usb', 'r_lcd', 'r_south', 'r_cc', 'r_misc', 'r_ui', 'r_gnd', 'r_planes'] if importlib.util.find_spec(m)]
for m in MODS:
    rt.NEWFRAME = False
    importlib.import_module(m)
print(rt.save(), len(rt.ITEMS))
