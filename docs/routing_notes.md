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

## Track widths (1 oz outer / 0.5 oz inner; IPC-2152 results in the section below)
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
- Length U1 → R2/R3 (track length, PlaceRoute fix round): **D+ 93.867 mm, D− 93.867 mm, skew 0.0002 mm**, matched with bumps
  on D+. **No layer changes** on USB_DP/USB_DN. On the connector side (USB_DP_C 11.41 mm / USB_DN_C 10.70 mm) only the J11
  B6/B7 contacts are tied over with two small vias, as the connector requires.
- Spacing: pair gap 0.20 mm everywhere; **no other F.Cu track within 0.68 mm** of the pair (nearest: CHG_CD). Other-net vias
  closer than 0.6 mm: GND stitching (31.0,−7.0) 0.32 mm (return-path via, intended); and three that were already there at
  a90341d: +3V3 (−38.0,3.35) 0.36 mm, CHG_CD (−45.2,3.25) 0.46 mm, SW3_IN (0.8,7.6) 0.52 mm. These are boxed in by
  the U2 bundle lanes and the SW4_IN via, so they stay where they are. The CHG_PG_N via added this round sits at
  (−32.0,3.0), 0.71 mm from the pair.
- **Impedance to confirm at order time:** W 0.19 / S 0.20 mm gives ≈ 90 Ω here, from our own stack-up numbers. Confirm it
  in JLC's impedance calculator for **JLC04161H-3313** (L1 over L2, 0.0994 mm prepreg) when ordering, and adjust W/S if JLC
  gives a different answer.

## Current paths, IPC-2152 (PlaceRoute fix round)
Method: the narrowest neck is the widest-path bottleneck through the net's copper on each layer, between the named terminals.
It is measured on the refilled zones plus tracks, pads and vias (`/tmp/neck.py`). Where a path runs on several layers in
parallel, the cross-section is the sum (In2 0.5 oz counts as half the width of 1 oz). ΔT is the IPC-2152 curve fit
A[mil²] = (117.555·ΔT^−0.913 + 1.15)·I^(0.84·ΔT^−0.018 + 1.159). Copper is 1 oz (35 µm) outer and 0.5 oz (17.5 µm) inner.
This is the long-conductor figure with no plane or spreading credit. For necks only a few mm long it overstates the rise, but it is
given as asked.

| Net (current) | Narrowest neck | Layer / copper | ΔT (fit) | Note |
|---|---|---|---|---|
| VBUS (3 A) | 0.30 mm × 2.4 mm | U16 pin 5 itself (F, 1 oz) | (pin) | pin-limited; the pour reaches the full pin length |
| VBUS (3 A) | 0.60 mm, ≈ 0.5 mm long | J11 A4/B9, A9/B4 pads → 2 vias (F, 1 oz) | 62 °C | the connector pad width; one via per pad pair |
| VBUS (3 A) | 1.90 mm (cross-section 3.87 mm) | In2 column J11 → y −13, ≈ 15 mm long (0.5 oz) | 32 °C (13 °C on the cross-section) | |
| VBUS (3 A) | 0.95 mm F + 3.0 mm B in parallel | F pour / B pour, via rows → U16 (≈ 13 mm) | 5.9 °C combined | 15 vias in the F pour |
| V5 (6 A) | 0.30 mm × 2.4 mm | U16 pin 6 (F) | (pin) | USB source only, ≤ 3 A |
| V5 (6 A) | 1.60 mm, ≈ 2 mm long | L1.2 → buck vias (F, 1 oz) | 112 °C | short; C75/C76 and 4 vias sit in it |
| **V5 (6 A)** | **1.30 mm widest path; total cross-section 4.39 mm** | **In2 west strip x −62.5…−57.6, buck → port band, ≈ 30 mm long (0.5 oz)** | **66 °C** on the cross-section | **open: see below** |
| Pack B_N (9 A) | 2.38 mm F + 2.38 mm In2 | BH1.2 lug → Q1 source (≈ 4 mm) | 108 °C | |
| Pack FET_D (9 A) | 5.40 mm F + 5.25 mm In2 | Q1 drain → Q2 drain | 33 °C | |
| Pack SNS_P (9 A) | 2.38 mm F + 1.30 mm In2 | Q2 source → R20.1 (≈ 3 mm) | ≈ 150 °C | |
| CELL2_P (9 A) | 3.50 mm F + 3.07 mm In2 | BH2.1 lug → F1.1 | 62 °C | |
| BAT+ (9 A) | 1.70 mm (F) | F1.2 → U17 pin 8 (≈ 3 mm), In2 strip in parallel only from C18 | off the fit (> 200 °C) | open |
| J5 / V5_5 (2.5 A) | 0.30 mm pin, then 0.97 mm | U14 pin 6 → J5.1/J5.2 pour (F) | 20 °C (pour) | pin-limited |
| J1–J4 / V5_1–4 (1 A each) | 0.30 mm pin, then 0.92 mm | U10–U13 pin 6 → Jn.1 pour (F) | 2.6 °C (pour), 9.4 °C at the pin | |

**Open item (needs a decision): the high-current paths do not meet a 10 °C IPC-2152 rise.** The worst are V5 at 6 A,
which has only the In2 west strip from the buck to the port band, and the pack path at 9 A (B_N / SNS_P / BAT+ necks).
- Why V5 is limited: the USBIN_FLT_N In2 lane at y −24 cuts the east channel, the VBUS In2 zone takes x −57.6…−44, and the
  J11 shield slots sit in the strip. Six GND stitching vias at x −61 were taken out of the strip this round, which raised the
  widest path from 0.72 to 1.30 mm.
- Possible fixes, not done this round because they go beyond a fix round:
  - move USBIN_FLT_N off In2 to open the east channel (≈ +4 mm);
  - add a B.Cu V5 strap along the west edge;
  - order 2 oz inner copper;
  - or derate the port total.

## Hot loops (PlaceRoute fix round)
Loop area is the polygon cap+ → IC pin → IC GND pin → cap−, on pad centres.
| Loop | Cap → pin (pad-edge gap / centre) | Area |
|---|---|---|
| U17 input, C73 (0402, closest) | C73.1 → U17.8 0.49 / 1.85 mm; C73.2 → U17.9 0.49 / 1.85 mm | 1.95 mm² |
| U17 input, C71 (bulk) | C71.1 → U17.8 1.58 / 3.40 mm; C71.2 → U17.9 1.58 / 3.35 mm | 5.11 mm² |
| U17 input, C72 (bulk) | C72.1 → U17.8' 1.26 / 2.44 mm; GND through the F pour | — |
| U2 PMID (input side), C8 | C8.1 → U2.22 0.60 / 1.76 mm; C8.2 → U2.19 0.60 / 1.74 mm | 2.95 mm² |
| U2 PMID, C9 | C9.1 → U2.22 2.60 / 3.75 mm | — |
| U2 boost output (SNS), C69 | C69.1 → U2.16 0.52 / 2.30 mm; C69.2 → U2.19 1.53 / 3.17 mm | 6.3 mm² |
| U2 SNS, C70 | C70.1 → U2.16 3.72 / 5.49 mm | — |

Switch-node copper:
- **BUCK_SW**: 16.0 mm² on F.Cu including the U17.6 and L1.1 pads, 3.3 mm² of pour and track besides the pads. Nothing else runs
  under it on F/B. BUCK_PG (In2) and PWR_HOLD (B) still pass under it; optional item 5 was not done.
- **CHG_SW**: 16.0 mm² F.Cu including pads (7.8 mm² of pour and track). Add 3.2 mm² on B.Cu and 0.6 mm² of via barrels: this is
  the 0.4 mm BTST-side link from U2.17/18 to C11.2, which runs on B because there is no F room.

## Sense routing (PlaceRoute fix round)
- **CSP / CSN (MAX17205 U15) are Kelvin-connected at R20.**
  - CSP: a 0.15 mm F stub leaves the R20.1 pad copper at (−15.9,−11.5), then via (−15.25,−11.5) → B.Cu north →
    via (−15.0,−9.0) → U15.2.
  - CSN: taken through the net tie **NT1** at the R20.2 pad (NT1.1 = GAUGE_CSN, NT1.2 = GND), F → via (−12.35,−10.4) →
    B.Cu (−12.35,−8.0) → (−15.0,−8.0) → via → U15.4.
  - Neither sense trace carries pack current, and both use their own vias. They run 3 mm apart on B, side by side over the solid In1 GND.
- **MID**: two B.Cu traces from the BH1.1 lug's MID pour (B + In2, x 37.6–44.4):
  - a 0.25 mm sense trace to R146 (BQ25887 MID) with a branch to R18 (S-8252 VC);
  - a separate 0.5 mm trace to the R147.2 F pour (CBSET balancing current, ≈ 110 mA), so the balance current doesn't
    run in the sense trace. The MID F pour at R147.2 is 29.8 mm² and has one feed via at (−35.4,−6.0), 0.73 mm east of
    the pad (not a via field, nothing under the body).
- **CBSET**: U2.10 → 0.15 mm F → the R147.1 pour (27.2 mm²). The CHG_PG_N vias are at (−34.6,−7.0) and (−32.0,3.0), both
  > 1 mm from the R147 outline.

## PlaceRoute fix round: bends and pad exits
- e5qc (updated rules) on a90341d → now:
  - CORNER 288 (F 141, B 88, In2 59) → **0**;
  - PADANGLE 159 (all F) → **0**;
  - TJUNC (report only) 34 (F 25, B 5, In2 4) → 31 (F 23, B 4, In2 4).
- Bends were fixed by script (`build/route/chamfer.py`): 45° chords, every one clearance-checked, plus hand-written square exits.
  Item 8 was cancelled, so the earlier T-junction chamfer/via passes were removed from the build (a clean revert); T's stay plain.
- No autorouter. No part moved this round.

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
  `e5qc` on a copy: PASS (viapad 0, angle45 0, corner 0, padangle 0; tjunc 31, report only).
- In1.Cu has 0 tracks. The U1 antenna keep-out is clear.
- Renders: `docs/images/routing_fcu.png`, `routing_in1cu.png`, `routing_in2cu.png`, `routing_bcu.png`,
  `routing_3d_top.png`, `routing_3d_bottom.png`.
