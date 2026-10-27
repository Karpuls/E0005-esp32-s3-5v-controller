# E0005 placement notes (for the placement / routing phase)

Inputs: SPEC v1.1 §5.6.1, §5.7, §9; schematic `E0005_controller.kicad_sch` (references below). Board: **≈ 125 × 65 mm, 4 × M3**, E0003 outline `E0005_mech:E0003_Outline_125x65_4xM3`, Keystone 1121 holders on the bottom. 4 layers JLC04161H-3313: L1 parts/signals/power pours, **L2 (In1) solid GND**, **L3 (In2) V5 + BAT+ pours** and slow signals, L4 GND + holder lugs + protection parts.

House rules: no test points; no vias on/under pads (≥ 0.15 mm via-to-pad copper, EP thermal vias exempt); tracks at multiples of 45°; JLC rules + no-via-on-pad in `E0005_controller.kicad_dru` (copied from E0003); 90 Ω USB pair. Placement with the KiStack `layout-placement` scripts; routing by hand/IPC only, **no autorouters**.

## Edge plan (E0003's, SPEC §9)
| Edge | Parts |
|---|---|
| **West** | J11 USB-C; D1 SMF9.0A and U4 USBLC6 at the connector; power stage off the cells: U16 (U_IN), U2 BQ25887 + L2 (1 µH IHLP-2525, 6.9 × 6.5 × 3.0 mm), U17 TPS56637 + **L1 (3.3 µH IHLP3232DZER3R3M11, 8.64 × 8.18 × 4.0 mm, footprint `L_Vishay_IHLP-3232`, the largest power part on top)**, U5 3V3 + L3 |
| **North** | J1–J4 (GH4), J5 (GH6); per port U10–U14 eFuse with its R/C, SMF5.0A (D19…D27) and TPD2E2U06 at the connector, 220 Ω between ESD and the mux side; silkscreen **"5V" + port number + "E0001"/"E0002"** at every port; a 10 µF/25 V at each eFuse input (C48/51/54/57/60). No separate port bulk any more (SPEC v1.1) |
| **East** | U1 ESP32-S3 with the antenna keep-out (≥ 15 mm to the cell cans) |
| **South** | J6–J9 switches, J12 + SW1 power button (D12, D13, D14 near SW1/J12), J10 EYESPI, BOOT/RESET |
| **Bottom** | BH1/BH2 holders, RT1/RT2 between the cells, F1, protection parts as E0003 |

## U_IN (U16) cooling copper reservation (SPEC §5.6.1)
- U16 on **F.Cu**, **≈ 15 × 12 mm keep area** including C65, R133–R141, C66, C67, Q11, Q12.
- **IN (VBUS) pins → F.Cu pour ≥ 80 mm²** (e.g. 10 × 8 mm) right at the pads; **OUT (V5) pins → F.Cu pour ≥ 80 mm²**, joined to the V5 rail.
- **≥ 6 vias per pour** (0.3 mm drill / 0.6 mm pad), each **≥ 0.15 mm copper-to-copper from any pad**: V5 pour → **In2 V5**, VBUS pour → **B.Cu VBUS pour ≥ 100 mm²**.
- **GND pin (8)** → In1 plane with **≥ 2 vias off the pad**.
- **Solid zone connection** (no thermal-relief spokes) on the U16 pads.
- Keep **U2 BQ25887, L2 (1 µH), L1 (3.3 µH) and U17 TPS56637 ≥ 5 mm** from the U16 keep area.
- The RPW package has no exposed pad: no vias under the part (house rule).

## Hot loops and Kelvin connections
**BQ25887 (U2, boost, 1.5 MHz)** — datasheet §10:
- **SNS caps C69/C70 (2 × 47 µF) closest to SNS (15/16) and GND (19/20)**: the boost output loop (SW → QHS → SNS → C → GND → QLS) is the critical one.
- **PMID caps C8/C9 next to PMID (21/22) and GND**, shortest copper; C2 (1 µF) at VBUS (23).
- L2 between PMID and SW (17/18) with a short, wide SW node; keep the SW copper small and away from TS/ILIM/MID.
- C11 (BTST) directly SW–BTST; C20 (REGN) at pin 11; C18 (BAT 10 µF) at BAT (13/14).
- EP (25) to In1 GND with thermal vias in the pad (exempt).
- R145 (ILIM), R10/R11 (TS) and PSEL/CD pull-ups on the quiet side, referenced to the GND pin.
- MID (R146 300 Ω) and CBSET (R147 39 Ω 2512, 0.45 W) run to the cell mid-point (MID net, cell holders): separate traces from the mid-point, ≥ 0.4 mm for CBSET (≈ 110 mA); give R147 some copper on both pads.
- BAT/SNS currents up to 2.2 A: BAT+ ≥ 1 mm or pour to F1/BH2.

**TPS56637 (U17, buck, 500 kHz, up to 6 A)** — datasheet §10:
- **Input loop:** C73 100 nF and C71/C72 10 µF between VIN (8) and PGND (9) as close as possible, same layer, no vias in the loop.
- **SW node (6) → L1** short and wide; C74 (BOOT) directly at pins 7–6.
- **Output caps C75/C76 (2 × 47 µF, the only V5 bulk, SPEC v1.1) at L1's output**, GND returns to PGND through the plane with several vias. L1 is 8.6 × 8.2 mm: reserve ≈ 10 × 10 mm for L1 + C75/C76 next to U17's SW pin.
- **FB divider R153/R154 and the FF network R155/C79 next to FB (2)**, sense V5 at the output caps (not the SW side); AGND (3) to PGND at a single point (plane via near pin 3).
- EN divider R151/R152 near EN (1); MODE (10) straight to AGND/GND.
- V5 path buck → C75/C76 → port eFuses: pours on two layers (L1 + In2) or ≥ 3 mm with via stitching (≈ 6 A).
- BAT+ → F1 → U17 VIN (≈ 5 A): pours on two layers or ≥ 3 mm.

**3V3 (U5)** as E0003 (C22 10 µF + C23 at VIN, L3, C24 at VOS).

**R_SENSE (R20, 5 mΩ 2512)** as E0003: pack path B_N → Q1 → Q2 → SNS_P → R20 → GND as wide pours (≈ 5–9 A). **Kelvin:** the gauge CSP tap (SNS_P) from the R20 pad itself, the CSN tap via NT1 at the R20 GND pad; route both as a pair to U15, away from the buck SW node.

## Other placement notes
- **Soft power latch** (Q13, R148–R152, Q14): near U17's EN; PL_PULL / PB_RAW are slow signals, but keep PB_RAW short and away from SW nodes (it idles at high impedance near BAT+).
- **CC sense** R131/R132 + C63/C64: the 1 nF at the ESP32 end (GPIO6/7); R129/R130 Rd at J11.
- **V5_SENSE** divider R142/R143 + C68 near the ESP32 (GPIO4), sensing V5 at the port eFuse group.
- USB D+/D−: 90 Ω differential, J11 → U4 → R2/R3 → GPIO19/20, as E0003.
- 10 µF/25 V at each port eFuse input (C48/51/54/57/60) and at the 3V3 input (C22).
