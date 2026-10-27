# E0003 mechanical footprints (Router, 2026-10-10)

Generator: Router's `e0003/gen_mech_fp.py`. 3D model: FreeCAD script `k1121.py`, simplified holder plus a P50B cell.

## `E0003_mech:Keystone_1121_1x21700_THM`: one per cell (BH1, BH2), placed on the **bottom** side
Source: Keystone catalogue K75 p.30, Cat. No. 1121 Polarized, THM mounting detail.
- Origin is the body centre. Body 82.2 × 23.1 mm; 74.0 mm cell bay; end walls 20.4/21.6 mm tall.
- **Pad 1 = +** at (+38.15, 0): the rib/positive end, rectangular pad. **Pad 2 = −** at (−38.15, 0): the spring end. Both are Ø1.3 mm plated holes on 2.8 mm pads, 76.3 mm apart.
- Locating holes, non-plated: Ø3.6 mm at (+27.6, −9.0) and (−27.6, +9.0); Ø2.4 mm at (+38.15, +9.0).
- Silkscreen "+" and "−" marks next to the lugs. F.Fab shows the P50B outline (70.15 × 21.55 mm).
- STEP: `lib/E0003_mech.3dshapes/Keystone_1121_P50B.step`, a simplified holder with a P50B cell. Overall height 22.75 mm (cell top), so the spec's ≥ 25 mm bottom standoffs are fine.
- Side by side at 25.1 mm pitch (2 mm gap), the pair covers 82.2 × 48.2 mm, as in the spec.
- **The P50B flat-top fit in the polarized holder must be tested on a sample before ordering (spec §11).** If it fails, the replacement holder needs a new footprint.

## `E0003_mech:E0003_Outline_125x65_4xM3`: board-only, placed by Router (no schematic symbol)
- Edge.Cuts 125 × 65 mm with R3 corners. 4 × M3 holes (Ø3.2 mm plated, 6 mm pad) 4 mm from each corner (§9.4).
- The size is a generator parameter (BX/BY), in case layout needs a few mm more for the antenna's 15 mm clearance from the cans.

## E0005 fix to the Keystone 1121 model and footprint (PlaceRoute, 2026-10-27)
- **3D model was mirrored in Y against the footprint.** The STEP had been drawn in footprint coordinates (Y down), but KiCad models use Y up. On the board, every locating peg landed 18 mm from its hole and poked through solid board. The model is now mirrored about the XZ plane. Exported from the board, all 3 pegs and both lugs on each holder sit centred in their holes (checked in FreeCAD).
- **Solder lugs were drawn as 0.6 × 4.0 mm blades,** which can't pass a Ø1.3 mm hole. They are now 0.5 × 0.9 mm pins, 3.4 mm long (1.8 mm above the top surface of a 1.6 mm board).
- **The footprint itself matches Keystone K75 p.30** (lugs Ø1.3 at 76.3 mm, pegs Ø3.6 at 55.2 × 18.0 mm, Ø2.4 at 10.53 mm from the Ø3.6). Unchanged.
- **New top-side keep-out rings** (B.CrtYd in the library, F.CrtYd once the holder is on the bottom): r 2.4 mm around each lug pad (soldering-iron access), r 2.3 mm around the Ø3.6 peg holes and r 1.7 mm around the Ø2.4 hole. DRC now flags top-side parts that crowd the lugs and pegs.
- Old model: `build/backup/Keystone_1121_P50B.step.pre-mirror-fix`. E0003 uses the same (mirrored) model; its footprint and fab data are not affected.
