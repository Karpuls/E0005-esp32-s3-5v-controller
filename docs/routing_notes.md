# E0005 routing notes

## Outline
- **Outline enlarged to 125 × 73 mm** (was 125 × 65) during routing, 2026-10-27, with the owner's OK. The 8 mm was added at the
  **north** edge: the J1–J5 port band (connectors, eFuses U10–U14 and their passives, Q3/Q5/Q7) and the U16 USB-input stage moved
  north with the edge; everything else, including BH1/BH2, U1 and the antenna keep-out, stayed put.
  Reason: the band between U8/U9 and the port eFuses was full on all three routing layers (only one free 0.15 mm lane on B.Cu across
  x 18–36), so the U9/U8 fan-out, I2C0, the port FLT/OFF/I2C lines and SW1..4_IN could not be routed cleanly.
- The 4 × M3 holes keep their 4 mm corner inset: OUT1 now uses `lib/E0005_board.pretty/Holes_4xM3_125x73` (same 3.2 / 6.0 mm plated
  holes as `E0005_mech:E0003_Holes_4xM3`, which is left unchanged). Corners stay R3.
- Part nudge for the move: Q3 +0.3 x / −0.3 y (clear of the BH1 peg ring).

## How it was routed
- By hand, as scripts sent to KiCad over IPC (`build/route/r_*.py` → `build.py` → `apply.py`); no autorouter of any kind.
  Every segment was clearance-checked before it was written (`probe.py`); the stitching grid (`stitch.py`) only filters
  a regular 4 mm grid for clearance.
- Stack-up JLC04161H-3313 (1.6 mm, 4 layers): **F.Cu** components and most signals; **In1.Cu** solid GND (no tracks);
  **In2.Cu** power planes (V5: west column + the north port band; 3V3: the rest) plus short or slow signal lanes;
  **B.Cu** signals and pours.
- All tracks are at 45° multiples. There are no vias on or under pads (≥ 0.15 mm via-to-pad copper gap; EP thermal vias
  exempt). The 3 mm hole pegs, holder rings and the U1 antenna keep-out are untouched.
- The F.Cu and B.Cu GND pours (0.21 mm clearance) are stitched to In1 with a 4 mm via grid (145 vias), plus vias next to each
  GND pad that a pour piece couldn't reach.
- Some In2 signal lanes split the 3V3 plane into pieces. Each piece is tied back to the main plane by short 3V3 bridges
  (two vias plus an F.Cu link, `r_fix.py`).

## Track widths (IPC-2152, 1 oz outer / 0.5 oz inner, ≤ 10 °C rise)
| Net / class | Current | Copper |
|---|---|---|
| VBUS (USB-C → U16/U2) | ≤ 3 A | F/B/In2 pours; 0.4–0.6 mm links (≤ 3 mm long) |
| V5 (U16 / buck → ports) | ≤ 6 A total; ports ≤ 1 A (×4) and 2 A | In2 V5 plane (band + west column), B.Cu V5 bus pour, F.Cu pours at each eFuse; 0.25–1.0 mm local links (cap / divider / sense) |
| BAT+ / B_N / FET_D / SNS_P (pack path) | ≤ 9 A discharge, 2.2 A charge | F/B/In2 pours, F1 and Q1/Q2 copper, R20 Kelvin sense 0.15 mm |
| CHG_SW, BUCK_SW, BUCK_SW_3V3 | switch nodes | short F.Cu pours, 0.4–0.5 mm |
| +3V3 | ≤ 1 A | In2 3V3 plane; 0.2–0.4 mm tracks |
| MID / CELL2_P (balancing, cell link) | ≤ 0.3 A | 0.25–0.5 mm and pours |
| GND | — | In1 solid + F/B pours |
| Signals | < 50 mA | 0.15 mm |
| USB_DP / USB_DN | — | 0.19 mm, 0.20 mm gap (90 Ω differential) |

## USB 2.0 pair (U1 ↔ R2/R3 ↔ U4 ↔ J11)
- Edge-coupled microstrip on F.Cu over solid In1 GND (L1–L2 prepreg 0.0994 mm, εr 4.1): **W 0.19 mm, S 0.20 mm,
  Zdiff ≈ 90 Ω**. The GND pours keep 0.3 mm from the pair (DRU rule `USB pour gap`).
- Length U1 → R2/R3: D+ 94.234 mm, D− 94.233 mm, **skew 0.001 mm (< 0.01 mm)**, matched with bumps on D+.
  **No layer changes** on USB_DP/USB_DN. On the connector side (USB_DP_C/DN_C, 11 mm) only the J11 B6/B7 contacts are
  tied over with two small vias, as the connector requires.

## Part nudges (all < 1 mm)
- R28 −0.60 x, R29 +0.50 x, R30 +0.50 x (U15 gauge fan-out); R98 0.60 north (U10 GND pin 8 exit); R85 0.60 west (port-3 EN via);
  Q3 +0.3 x / −0.3 y (with the outline move, clear of the BH1 peg ring).
- No other part moved. The north band parts moved 8 mm with the outline, as described above.

## DRC exceptions and rules added during routing
- `lib_footprint_mismatch` on U1 (ESP32-S3-WROOM-1 local override): accepted, as before.
- DRU `USB pour gap` (0.3 mm, USB pair to pours) and `U17 pour corner` (0.18 mm, pour against U17 pads: pin 1 is 0.23 mm
  from GND pin 10 by the footprint, and the solid pour on pin 10 came 3 µm under 0.2 mm; JLC minimum is 0.09 mm).

## Status
- DRC (schematic parity, all severities, zones refilled): 0 errors, 0 unconnected, 0 parity; only the U1 exception.
  `e5qc` on a copy: PASS (viapad 0, angle45 0, acute 0).
- Renders: `docs/images/routing_fcu.png`, `routing_in1cu.png`, `routing_in2cu.png`, `routing_bcu.png`,
  `routing_3d_top.png`, `routing_3d_bottom.png`.
