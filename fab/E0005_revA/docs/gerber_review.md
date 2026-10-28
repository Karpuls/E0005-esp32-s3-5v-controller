# E0005 rev A gerber review

Every image here is rendered **from the fab files themselves** (`gerbers/*.g*`, `*.drl`) with pygerber 2.4.3. They are not board plots. All layers are placed on one frame (the Edge.Cuts extent, 20 px/mm) so the checks can be measured, not only looked at.

- Script: `build/scripts/gerber_review.py`, run by `build/scripts/fab_export.sh`.
- Numbers: `docs/gerber_review/gerber_review.json`.
- Source board: SOURCE_COMMIT.

Colours:
- copper is orange, holes are black;
- the antenna keep-out is **blue where it is empty** (copper there would show red);
- mask openings are gold and silk is white;
- vias are circled cyan on the mask/via images.

## Results

| # | Check | Result | Image |
|---|---|---|---|
| 1 | Copper on each layer matches the board renders `docs/images/routing_*.png` | **PASS.** Each layer was compared by eye with its board render: same pours, track bundles, via grid and planes. Copper coverage inside the outline: F 78.9 %, In1 92.5 %, In2 74.3 %, B 81.6 %. The In2 north strip (y 59.5–67) and the east strip are empty in both the gerber and the board render: no In2 zone there by design | `gerber_review/gerber_F_Cu.png`, `gerber_In1_Cu.png`, `gerber_In2_Cu.png`, `gerber_B_Cu.png` |
| 2 | **In1 is solid GND** | **PASS.** In1 has 344 voids inside the outline. Every one lies within 1 mm of a drill hit (a via antipad or through-hole clearance) or is the 0.3 mm edge pullback. **0 voids elsewhere** and no tracks | `gerber_In1_Cu.png` |
| 3 | **Antenna keep-out clear** (rule area x 206.05–212.6, y 76–124, all copper layers) | **PASS.** **0 copper pixels** inside the keep-out on F, In1, In2 and B (measured 0.1 mm inside its border). Only U1's silk outline and refs are near it | `gerber_zoom_antenna.png` (all 4 copper layers merged) |
| 4a | Mask openings on pads only | **PASS.** F.Mask has 858 openings and B.Mask 24. Every opening has copper under it, except the 8 NPTH holes (USB-C pegs, holder pegs), which is correct | `gerber_F_mask_silk.png`, `gerber_B_mask_silk.png` |
| 4b | **Vias tented** | **PASS** for the mask settings: the board has tenting front/back = yes, and 682 vias have **no mask opening of their own** on either side. 9 vias sit inside a pad opening:<br>- U2 EP: 6 vias (exempt EP thermal vias);<br>- U15 EP: 2 vias (exempt EP thermal vias);<br>- **one V5 via in L1's pad 2: see finding F-1** | `gerber_F_mask_vias.png`, `gerber_B_mask_vias.png` |
| 4c | Via-to-pad gap ≥ 0.15 mm (owner rule), measured from the gerbers | **5 exceptions, see finding F-2.** On B, 0 vias are closer than 0.15 mm to a pad | `gerber_F_mask_vias.png` |
| 5a | Silkscreen legible, nothing on pads | **PASS.** Text is legible on both sides, and the bottom side is mirrored correctly (holder outlines, CELL ± labels, the "2 x 21700 P50B" and board-name lines). Silk inside openings: F 386 slivers, each ≤ 8 px (≤ 0.02 mm², the raster edge where KiCad subtracted the mask from the silk); B 0. No silk outside the board | `gerber_F_mask_silk.png`, `gerber_B_mask_silk.png` |
| 5b | **"5V" next to every port J1–J5** | **PASS.** "5V Jn E0001" (J1–J4) and "5V J5 E0002" are present beside each connector (text at x 122.7 / 137.2 / 151.7 / 166.2 / 182.15, y 64.1; 616–678 silk px each) | `gerber_zoom_ports_5V.png` |
| 6 | Board outline 125 × 73 mm, R3 corners, slots | **PASS.** Edge.Cuts is one closed outline, 125.1 × 73.1 mm over the 0.1 mm line, so **125.0 × 73.0 mm**. Corner radius measured at 3.07 mm (R3). J11's 4 shell slots are **plated 0.6 mm oval slots** in the PTH file (at x 90.50 / 94.83, y 100.18 / 108.82). There are no routed slots in Edge.Cuts | `gerber_zoom_J11.png`, `gerber_drill.png` |
| 7 | Drills | **PASS.**<br>- PTH: 682 × 0.30 (vias), 4 × 0.60 slots (J11 shell), 4 × 0.80 (NTC leads), 4 × 1.30 (holder lugs at x 114.85 / 191.15, y 86.95 / 113.05), 4 × 3.20 (M3 at 4 mm corner inset).<br>- **NPTH**: 2 × 0.65 (USB-C pegs), **2 × 2.40 and 4 × 3.60 (holder locating pegs)**, all non-plated. | `gerber_drill.png` (green PTH, red NPTH); `reports/E0005_revA_drill_report.txt` |
| 8 | Paste | F.Paste on SMD pads only. **B.Paste is empty**, which is correct: the bottom side has only the through-hole BH1/BH2 and RT1/RT2 | `gerber_paste.png` |

## Findings (board, not fixed here)

**F-1. V5 via inside L1 pad 2 (via in pad, not an EP).**
- Via V5 0.6/0.3 at (100.6, 124.6). L1 (IHLP-3232) pad 2 spans x 100.13–105.47, y 123.3–125.7.
- The via centre is 0.47 mm inside the pad edge, so the hole is in the solder joint: solder wicks down the barrel, and the via isn't tented.
- DRC doesn't flag it because via and pad share the net (the `Router via to pad` rule only catches different nets), and the routing check `e5qc` reported viapad 0.
- Owner rule: "no vias on or under pads (EP thermal vias exempt)". **Lead decision:** move the via ≥ 0.45 mm (centre) off the pad edge, or accept it (it would then need filling/capping or a paste reduction).

**F-2. Five FET_D vias at the edge of Q2's drain tab.**
- Vias FET_D at (124.75, 85.0 / 86.0 / 87.0 / 88.0 / 89.0).
- They sit between Q1's drain-tab opening (ends x 124.40) and Q2's drain-tab opening (starts x 124.95). Via copper spans x 124.45–125.05: **0.10 mm into Q2's tab opening**, and 0.05 mm from Q1's.
- Same net as both tabs, so DRC passes.
- These are the In2 FET_D current vias (routing notes: FET_D In2 5.25 mm). The LFPAK56 drain tab is the FET's thermal pad, so they can be read as exempt thermal vias. But they are partly exposed: a via barrel edge inside a pad opening can wick solder off the tab.
- **Lead decision:** accept as drain-tab thermal vias, or shift the column (the 0.55 mm gap between the two tabs can't hold a 0.6 mm via with 0.15 mm each side, so the fix is to move the vias fully inside the tab with a capped/filled via, or to drop them and rely on the F pour).

## Notes
- pygerber 2.4.3 draws KiCad's RoundRect aperture macros correctly in this export (the E0003 run needed a macro-free fallback; this one doesn't).
- The JLC gerbers are plotted with **no X2**, Protel extensions and "subtract soldermask from silkscreen", with zones refilled (`--check-zones`). The drill is metric Excellon, decimal, absolute origin, with PTH and NPTH in separate files and drill maps (Gerber X2) in `reports/`.
