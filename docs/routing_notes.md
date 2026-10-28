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
| V5 (U16 / buck → ports) | 4.6 A design; ports 1 A (×4) and 2.5 A | In2 V5 plane (band + west column), B.Cu west-edge V5 strap + V5 bus pour, F.Cu pours at each eFuse; 0.25–1.0 mm local links (cap / divider / sense) |
| BAT+ / B_N / FET_D / SNS_P (pack path) | 5 A design (9 A fault only, until F1 opens); 2 A charge | F/B/In2 pours, F1 and Q1/Q2 copper, R20 Kelvin sense 0.15 mm |
| CHG_SW, BUCK_SW, BUCK_SW_3V3 | switch nodes | short F.Cu pours, 0.4–0.5 mm |
| +3V3 | ≤ 1 A | In2 3V3 plane; 0.2–0.4 mm tracks |
| MID / CELL2_P (balancing, cell link) | ≤ 0.3 A | 0.25–0.5 mm and pours |
| GND | — | In1 solid + F/B pours |
| Signals | < 50 mA | 0.15 mm |
| USB_DP / USB_DN (+ _C) | — | 0.153 mm, 0.20 mm gap (90 Ω differential, JLC calculator) |

## USB 2.0 pair (U1 ↔ R2/R3 ↔ U4 ↔ J11)
- Edge-coupled microstrip on F.Cu over solid In1 GND, JLC04161H-3313 (L1 over L2, prepreg 0.0994 mm): **W 0.153 mm,
  S 0.20 mm** (centre pitch 0.353 mm). This is **90 Ω, confirmed in JLC's impedance calculator** by the owner on 2026-10-28:
  coplanar differential with a 0.30 mm (11.8 mil) gap to copper gives W = 6.02 mil = 0.153 mm at S = 7.87 mil
  (non-coplanar gives 6.05 mil). The earlier 0.19 mm width came out at ≈ 80 Ω.
  The GND pours keep 0.30 mm from the pair (DRU rule `USB pour gap`).
- Length U1 → R2/R3 (track length): **D+ 93.851 mm, D− 93.852 mm, skew 0.001 mm**, matched with three bumps on D+.
  The pair sits at exactly 0.200 mm gap for 88.6 % of the D− length; the rest is the bumps and the U1 / R2 / R3 pin
  fan-outs. **No layer changes** on USB_DP/USB_DN.
- Connector side (USB_DP_C 11.41 mm / USB_DN_C 10.70 mm, J11 → U4 → R2.1/R3.1): also 0.153 mm, including the J11 B6/B7 tie
  links and their two small via pairs, as the connector requires. The pad geometry sets the spacing here (minimum gap
  0.34 mm). The pads (J11 A6/A7 0.3 mm, U4 pins, R2/R3) are all wider than the track, so there are no neck-downs.
- Spacing: no other F.Cu track within 0.70 mm of the pair. Other-net vias closer than 0.6 mm:
  - GND stitching at (31.0,−7.0), a return-path via;
  - three from a90341d: +3V3 (−38.0,3.35), CHG_CD (−45.2,3.25), SW3_IN (0.8,7.6). These are boxed in by the U2 bundle
    lanes and the SW4_IN via.

## Current paths, IPC-2152 (design currents per the owner, 2026-10-28)
Design currents:
- pack path 5 A (buck input at 6 A out from a 6.4 V pack; the 2 A charge never flows at the same time; 9 A only in a fault, until F1 opens);
- V5 4.6 A (ports 4.4 A + the 3V3 rail);
- VBUS 3 A;
- J5 2.5 A;
- J1–J4 1 A each.

Method:
- **Cross-section** is the smallest total copper width across the current path on refilled zones, summed over the layers in
  parallel, with In2 (0.5 oz) counted at half width (`/tmp/xcomb.py`, `/tmp/vcomb.py`).
- **Neck** is the widest-path bottleneck on one layer (`/tmp/neck.py`).
- ΔT is the IPC-2152 curve fit A[mil²] = (117.555·ΔT^−0.913 + 1.15)·I^(0.84·ΔT^−0.018 + 1.159), on 1 oz-equivalent copper
  (35 µm outer, 17.5 µm inner).
- This is the long-conductor figure with no plane or spreading credit, so it is conservative for the short necks.

| Net (design current) | Smallest cross-section (1 oz equivalent) | Where | ΔT (fit) |
|---|---|---|---|
| **V5 (4.6 A)** | **4.65 mm** = In2 7.14 mm + B.Cu strap 1.08 mm | at the J11 shell slots (y ≈ 0), the narrowest place on the buck → port band path | **12.7 °C** |
| V5, rest of the column | In2 ≥ 9 mm + B.Cu strap 2.85–4.15 mm | y −30 … +12 | < 9 °C |
| Pack BAT+ (5 A) | 5.44 mm (F) | F1.2 → U17 VIN pins (pour between them) | **12.8 °C** |
| Pack BAT+ at the pins | 2.1 mm | the U17 pin-8 column itself (pin-limited, < 0.6 mm long) | (pin) |
| Pack SNS_P (5 A) | 4.3 mm F + 3.8 mm In2 (eq 6.2 mm); F alone 4.3 mm | Q2 source pins → R20.1 (≈ 1.1 mm long) | **11.0 °C** (≈ 17 °C on F alone) |
| Pack B_N (5 A) | 4.05 mm F + 4.05 mm In2 (eq 6.07 mm) | BH1.2 lug → Q1 source | 11.3 °C |
| Pack FET_D (5 A) | 5.40 mm F + 5.25 mm In2 (eq 8.0 mm) | Q1 drain → Q2 drain | 8.2 °C |
| CELL2_P (5 A) | 6.65 mm F + 6.1 mm In2 (eq 9.7 mm) | BH2.1 lug → F1.1 | 6.9 °C |
| VBUS (3 A) | In2 3.87 mm (0.5 oz) | J11 → y −13 column | 13.3 °C |
| VBUS (3 A) | 0.95 mm F + 3.0 mm B (eq 3.95 mm) | via rows → U16 pin 5 | 5.9 °C |
| VBUS (3 A) | 0.60 mm, ≈ 0.5 mm long | the J11 A4/B9 and A9/B4 pads → their via | (connector pad) |
| J5 / V5_5 (2.5 A) | 0.97 mm (F) | U14 pin 6 → J5.1/J5.2 pour; the pin itself is 0.30 mm wide | 20.0 °C (pour) |
| J1–J4 / V5_1–4 (1 A each) | 0.92 mm (F) | U10–U13 pin 6 → Jn.1 pour; the pin itself is 0.30 mm wide | 2.6 °C (pour), 9.4 °C at the pin |

Changes made for these numbers (2nd review of the fix round):
- **USBIN_FLT_N** now crosses the In2 V5 west column on F.Cu (vias at (−39.0,−24.0) and (−44.6,−24.0)). Before, its In2 lane
  at y −24 cut the column down to the west strip alone (4.39 mm).
- **B.Cu V5 strap** `R_V5_STRAP_B` runs along the west edge from the buck area (y +12) to the port band. It is 4.15 mm wide for
  y −30…−7, 2.85 mm for y −7…+9, and 1.0 mm past each J11 shell slot pair.
  - North end: a B block over the 14 U16 V5-pour vias, overlapping `R_V5BUS_B`.
  - South end: 6 vias to In2 V5, plus 8 more along the strap.
  - Three GND stitching vias were removed to make room ((−61,5), (−61,−31), and the six at x −61 from the first pass).
  - The strap stays west of the +3V3 / CHG_STAT B lanes and the C1/R1 GND via.
- **SNS_P** F pour widened north (to y −10.0) and south (to y −14.75 east of Q2.4). The In2 copper only carries current past
  the via column at x −17.55, because Q2's source pins leave no room for vias between them, so the F figure is the one
  that counts.
- **BAT+**: no change needed. The pour is 5.44 mm wide between F1.2 and U17. The 2.1 mm figure from the first pass was the
  U17 VIN pin column itself, which no copper change can widen.

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

## Same-net via-in-pad sweep (fab review F-1 / F-2, 2026-10-28)
Every via was checked against every same-net pad's copper box; the gap must be ≥ 0.15 mm unless the pad is an EP.
- **F-1:** the V5 via at (−49.4,24.6) sat inside L1 pad 2. It is replaced by three vias at x −43.45 (y 23.6, 24.6, 25.5),
  between L1.2 and C76, in the V5 F pour. That makes 6 V5 vias at the buck output with the three at x −38.9. The F neck
  from L1.2 to the new vias is 2.6 mm. The V5 path is unchanged at 12.8 °C at 4.6 A.
- **F-2:** the five FET_D vias in the 0.55 mm gap between the Q1 and Q2 drain tabs are replaced by **six** vias in a row at
  y −15.75 (x −27.8 … −23.3), 0.20 mm north of both tabs. The F and In2 FET_D pours were extended to y −16.3 to cover them.
  The south end is taken by the CHG_G B.Cu lane and the B_N In2 lane. FET_D is now 67.5 mm² on F and 67.8 mm² on In2, with
  8.1 °C at 5 A across the pack path.
- After the fix: the only same-net vias touching a pad are the EP thermal vias of U2 (EP pin 25, 6 vias) and U15 (EP pin 15,
  2 vias). Closest same-net non-EP gaps: GND via (1.95,−34.10) to C54.2 and EXP_INT_N via (35.60,5.71) to U1.25, both
  exactly 0.150 mm. Different-net via-to-pad gaps are covered by DRC and e5qc viapad (0).

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
