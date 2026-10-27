# E0005 schematic capture notes (Phase 2, 2026-10-27)

**Spec:** `docs/SPEC.md` **v1.1** (v1.0 + lead review of 0babac7: TPS56637 L/C per datasheet Table 4, port UVLO 1 M / 402 k, PWR_HOLD rule §8.5, low-pack derating §8.6). Reference design: E0003 (copied, not edited).

**Root:** `E0005_controller.kicad_sch`, 4 hierarchical sheets, 269 symbols (268 BOM parts + net tie NT1):

| Page | File | Content |
|---|---|---|
| 2 | `power.kicad_sch` | USB-C J11, CC Rd + CC sense, SMF9.0A, USBLC6, **U_IN** TPS259470A (U16) with the 3-level R_ILM legs, **BQ25887** (U2), **TPS56637** (U17) + soft power latch, V5_SENSE, TPS629210 3V3 (U5) |
| 3 | `battery.kicad_sch` | cells BH1/BH2, F1, reverse-cell LEDs, NTC1/NTC2 (RT1/RT2), S-8252AAG + Q1/Q2, R_SENSE R20, MAX17205 (U15) |
| 4 | `mcu.kicad_sch` | ESP32-S3-WROOM-1-N16R2, BOOT/RESET, LEDs, power button SW1 + J12, J6–J9 switch inputs, J10 EYESPI |
| 5 | `ports.kicad_sch` | PCA9548APW, TCA9535 (SPEC §5.10 map), 5 × TPS259470A ports J1–J5, V5 bulk |

**Generated** by `build/scripts/gen_sch.py` (core `sch_core.py`, deterministic UUIDs), started from E0003's generator. **Edit the generator, not the .kicad_sch files.**
- `build/scripts/make_symlib.py` writes `lib/E0005.kicad_sym` and `lib/E0005.pretty` (E0003's symbols/footprints + the new TPS56637 symbol and TI RPA0010A footprint). `lib/E0005_mech.*` are E0003's holder/outline libraries, renamed.
- Libraries: `E0005` / `E0005_mech` in `sym-lib-table` / `fp-lib-table`; all `E0003:` references rewritten.

**Checks** (all re-run after every change):
- `build/scripts/render_check.sh`: ERC (`--severity-all`) **0 errors, 0 warnings** (report: `build/E0005_erc.rpt`), netlist, PDF, connectivity report. Unlabelled nets are only the deliberate wired chains: R–LED (D2, D3/D4, D5/D6, D11), the U_IN leg R–FET drains (Q11, Q12), Q_PL gate/drain (Q13) and the buck feed-forward R–C.
- `build/scripts/check_fp.py`: all 269 footprints exist; pin numbers = pad numbers for all 39 symbol/footprint pairs.
- `build/scripts/check_refs.py`: every reference shared with E0003 is the same part, except the intended changes listed below.
- `build/scripts/make_bom.py` writes `bom/E0005_digikey_bom.csv` from the schematic fields.
- Net-by-net audit done from the netlist for every new circuit (U_IN, legs, charger, buck, latch, CC, V5_SENSE, TCA9535 map, ESP32 pins).

## Reference designators
E0003 references are kept for every part that stays (same generation order; removed parts leave their numbers unused). New parts are numbered above E0003's highest: R129–R155, C63–C76 + C79 (C77/C78 left unused after v1.1), Q11–Q14, U16, U17, L2.
- **Same ref, changed part (role unchanged):** U2 BQ25798 → **BQ25887**; D1 TVS2200 → **SMF9.0A**; D12 PESD5V0L1UL → **TPD1E10B09** (see D-4, L-3); D13 (was QON diode) → latch diode; D19/21/23/25/27 SMF9.0A → **SMF5.0A**; port dividers R95/R102/R109/R116/R123 232k → **402k** (SPEC v1.1), R97/R104/R111/R118/R125 137k → **249k**; C48/51/54/57/60 100 nF → **10 µF/25 V** (SPEC §5.1.1); C22 4.7 µF → **10 µF/25 V** (3V3 input, SPEC §5.1.1); **L1 is the 5 V buck inductor, now 3.3 µH IHLP3232DZER3R3M11** (SPEC v1.1; the lead's change list calls it "L2": in the schematic L1 = buck 3.3 µH, L2 = charger 1 µH); R60 DNP 0R now GPIO37 → GP1.
- **Removed:** C61/C62 (E0003's port bulk 2 × 47 µF, SPEC v1.1), U3 STUSB4500, U7 BQ29209, Q8–Q10, the BQ25798 support parts, MID divider (R33/R34/C34), PD_ALERT_N pull-up R39, GP2 option R61, P06 pull-up R91.
- **New:** U16 = U_IN (SPEC had no ref), U17 = TPS56637 (SPEC planned "U4", which is the USBLC6 in E0003), L2 = 1 µH, Q11/Q12 = U_IN legs A/B, Q13 = Q_PL, Q14 = PWR_HOLD FET.

## Checklist (SPEC §11 + PlaceRoute)

### 1. BQ25887 reference circuit (SLUSD89B §9.2, Fig. 69) — done
| Item | Value | Datasheet |
|---|---|---|
| VBUS cap | C2 1 µF/50 V 0603 | "≥ 1 µF at VBUS" |
| PMID caps | C8, C9 2 × 10 µF/25 V 0805 | ≥ 10 µF after derating total on VBUS+PMID, 25 V preferred (§9.2.2.2); ≈ 9 µF effective at 5 V + C2 |
| Inductor | **L2 1 µH IHLP2525CZER1R0M01**, 11 A rated / 22 A Isat, 10 mΩ | PMID → SW (Fig. 69). Isat ≥ I_IN + ripple/2: 3.3 A + 0.6 A ≈ 3.9 A ≪ 22 A |
| BTST | C11 47 nF/50 V (SW–BTST) | 47 nF |
| SNS | 2 × 47 µF/16 V X5R 1210 (C69, C70, E0003 common part) | "44 µF on SNS"; ≈ 45 µF effective at 8.4 V (SPEC asked 2 × 22 µF ≥ 16 V; no common 22 µF/16 V part, see D-1) |
| BAT | C18 10 µF/25 V | ≥ 10 µF |
| REGN | C20 4.7 µF/25 V 0603 | 4.7 µF |
| TS | R10 5.23k (REGN) / R11 30.1k (GND) ∥ RT1 103AT-2 | Eq. 1/2 give 5.24k / 30.31k for 0–60 °C. Check: 0 °C (27.28k) → 73.2 % of REGN (VT1 73.25 %); 60 °C (3.02k) → 34.4 % (VT5 34.375 %) |
| ILIM | R145 374 Ω 1 % | I_INMAX = 1110 / 374 = **2.97 A** hardware cap; register IINDPM lower |
| PSEL | R144 10k to 3V3 | high → 500 mA default (USB host) |
| CD | R12 10k to 3V3, TCA9535 P05 | high = HIZ: **charging off at reset** (internal 900k pull-down overridden) |
| MID | R146 300 Ω → cell mid-point | Fig. 69 note (bottom-cell reverse plug-in) |
| CBSET | R147 **39 Ω 1 % 2512 1 W** (RMCF2512FT39R0) | I_CB = 4.2 / (39 + 1 Ω R_DS(on)) ≈ **105 mA** (SPEC ≈ 108 mA); P = 0.105² × 39 = **0.43 W** in a 1 W part |
| STAT / PG / INT | STAT → amber LED + 1k from 3V3; PG → P16 (10k up, ports sheet); INT → GPIO5 (10k up, MCU sheet) | open drain, ≤ 6 V |
| I²C | I2C0, 0x6A; 2.2k pull-ups (MCU sheet, as E0003) | datasheet example uses 10k; 2.2k is within spec |

- **BAT and SNS:** BAT (13/14) = BAT+ after F1. SNS (15/16) is the boost output in front of the internal R_SNS, so it only gets its caps (Fig. 69). SPEC §5.4 "BAT+ feeds BQ25887 BAT/SNS" is read that way.
- **CD high, no battery:** HIZ, REGN off, QBLK off; VBUS draws ≤ 38 µA. Nothing reaches BAT+ from the charger.
- **CD low, no battery** (firmware must not do this, SPEC §8.4): the converter starts, IBAT_DISCHG probes for a battery, STAT blinks, and BAT+ can rise to ≈ VBUS − 0.4 V through the QHS body diode ≈ 4.6 V: still below the buck EN start threshold (≥ 5.0 V even at the lowest EN threshold), so V5 is not affected.
- **Buck back-feed (no battery, USB on):** V5 → L1 → TPS56637 high-side body diode → BAT+ ≈ 4.3 V (µA loads only: BQ25887 BAT ≈ 12 µA, MAX17205 VBATT, C18/C71–C73). The BQ25887 may wake its I²C from BAT (V_BAT_UVLO 3.7–4.42 V): harmless. The gauge reads ≈ 4.3 V pack with no cells, which fails the firmware battery-present test (pack 5.0–8.6 V and both cell readings 2.5–4.3 V), so charging stays off.
- **Ground offset:** BQ25887 GND = board GND; the pack minus reaches GND through Q1/Q2 + R_SENSE (≈ 9 mΩ, ≈ 20 mV at 2 A). CB_CHG_DIS = 1 (default) pauses charging during cell measurement, as SPEC §5.3.

### 2. TPS56637 FB and EN dividers, output filter (SPEC v1.1 §5.7, datasheet SLVSEG1A Table 4) — done
- **FB:** R153 **69.8k** / R154 **10.0k** (1 %): V_OUT = 0.6 × (1 + 6.98) = **4.788 V** (−0.25 % vs 4.80 V). V_FB ±1.5 % over temperature → 4.72–4.86 V, inside SPEC D1 (4.70–5.25 V). (14.3k had 0 stock: D-2, accepted.)
- **Inductor (v1.1): L1 3.3 µH Vishay IHLP3232DZER3R3M11** (the datasheet's own part, §8.2.2.2): 10.5 A rated, **9.7 A Isat**, 14.9 mΩ max, 8.64 × 8.18 × 4.0 mm, KiCad `Inductor_SMD:L_Vishay_IHLP-3232`; DigiKey 541-1352, 5 904 in stock. Ripple at 8.4 V in: 4.79 × 3.61 / (8.4 × 3.3 µH × 500 kHz) = **1.25 A p-p**; peak at 6 A = 6.6 A < 9.7 A Isat; I_RMS ≈ 6.0 A < 10.5 A.
- **Output capacitance (v1.1):** 2 × 47 µF/16 V 1210 at the buck output (C75, C76) + the 10 µF/25 V caps at the five port eFuse inputs and the 3V3 input. E0003's port bulk C61/C62 and v1.0's C77/C78 are removed. Effective value (table below) **≈ 85–88 µF, inside Table 4's 20–100 µF**. LC double pole 1/(2π√(3.3 µH × 88 µF)) ≈ 9.4 kHz (Table 4 corners: 8.8 kHz at 100 µF, 19.6 kHz at 20 µF).
- **Feed-forward:** R155 **20k** + C79 **100 pF** across R153. Table 4 (5 V row) gives R8 20 kΩ, C9 100–220 pF. The datasheet's own design (Fig. 17, §8.2) uses 100 pF with R6 = 73.2k. Our R6 = 69.8k puts the FF zero within 5 % of it (1/(2π × 69.8k × 100 pF) ≈ 22.8 kHz vs 21.7 kHz), and C_OUT sits mid-range, so 100 pF follows the datasheet design. 220 pF stays the bench option if the load step rings.
- **EN UVLO** (SLVSEG1A §7.3.4, Ip 1 µA, Ih 4 µA, V_EN rising 1.18 V typ / 1.26 V max, falling 1.12 V typ / 1.04 V min): R151 **200k** (from Q_PL drain) / R152 **53.6k** to GND.
  - Start: 1.18 + 200k × (1.18 / 53.6k − 1 µA) = **5.38 V** typ (**5.76 V** at V_EN 1.26 V).
  - Stop: 1.12 + 200k × (1.12 / 53.6k − 5 µA) = **4.30 V** typ: 1.08 V hysteresis (> 0.5 V recommended).
  - EN at 8.4 V, running: (8.4 / 200k + 5 µA) / (1/200k + 1/53.6k) = **1.99 V** (≤ 5.5 V recommended, 6 V abs max).
  - Latch off: EN = 1 µA × 53.6k = 54 mV. Divider current when on: 8.4 V / 254k = 33 µA; zero when the latch is off.
- **MODE → GND** (≤ 10 kΩ) → Eco-mode: no negative inductor current, so the buck never sinks from V5 when USB holds V5 above 4.79 V.
- **PG** → TCA9535 P17, 10k to 3V3 (< 5.5 V). PG is low whenever EN is low with VIN present (Table 2): firmware reads it only while the buck is meant to run.
- **Input / boot:** VIN 2 × 10 µF/25 V + 100 nF (C71–C73, ≥ 8.4 V rating); BOOT C74 100 nF/50 V X7R (≥ 10 V).
- **OVP:** 125 % × 4.79 V ≈ **6.0 V**, above USB's 5.5 V maximum on V5, so **USB holding V5 high never trips it** (at 5.5 V, FB is at 114.6 %, also just under the 115 % PG upper threshold). Only a faulty source between 6.0 V and U_IN OVLO (5.85–6.25 V) could trip it (non-latched, 25 ms hiccup).
- **SW discharge (was O-2): closed as SPEC v1.1 §8.5 and §13.** The 200 Ω SW discharge (§7.3.9) is on whenever EN is low with VIN present. Firmware keeps PWR_HOLD high while USB is attached and a battery is fitted. The ≈ 25 mA loss in USB-only / no-battery is accepted (see the back-feed section). The bench temperature check stays open (O-2b).

**V5 effective capacitance (v1.1).** DC-bias data: Samsung's characterization data for **CL32A476KOJNNNE** (product.samsungsem.com, DC bias 120 Hz / 0.5 Vrms, 25 °C): −39.2 % at 4.79 V, −41.2 % at 5.0 V. For the **10 µF/25 V X5R 0805 (TMK212BBJ106MG-T)**, Taiyo Yuden's curve download was not reachable from here, so the Samsung curve of the equivalent **CL21A106KAYNNNE** (10 µF/25 V X5R 0805) is the proxy: −48.3 % at 4.79 V, −50.3 % at 5.0 V. The 100 nF X7R is taken at −10 %. The U_IN output side adds nothing: U16 OUT has no cap of its own and sits on this V5 net.

| Part | Refs | Qty | Nominal | Eff. each @ 4.79 V (battery) | Eff. each @ 5.0 V (USB) | Total @ 4.79 V | Total @ 5.0 V |
|---|---|---|---|---|---|---|---|
| 47 µF/16 V X5R 1210 CL32A476KOJNNNE (buck output) | C75 C76 | 2 | 94 µF | 28.6 µF | 27.6 µF | 57.2 µF | 55.3 µF |
| 10 µF/25 V X5R 0805 TMK212BBJ106MG-T (port eFuse inputs) | C48 C51 C54 C57 C60 | 5 | 50 µF | 5.17 µF | 4.97 µF | 25.8 µF | 24.9 µF |
| 10 µF/25 V X5R 0805 TMK212BBJ106MG-T (3V3 input) | C22 | 1 | 10 µF | 5.17 µF | 4.97 µF | 5.2 µF | 5.0 µF |
| 100 nF/50 V X7R 0402 (3V3 input) | C23 | 1 | 0.1 µF | 0.09 µF | 0.09 µF | 0.1 µF | 0.1 µF |
| **Total on V5** | | 9 | 154 µF | | | **88.3 µF** | **85.3 µF** |

- At nominal tolerance: **85–88 µF ≤ 100 µF** (lead target 85–95 µF), and ≈ 85 µF at 5.0 V matches SPEC v1.1 §5.1.1's design value.
- With every cap at its upper tolerance (47 µF +10 %, 10 µF +20 %) the total reaches 96.6 µF at 5.0 V and 100.2 µF at 4.79 V: the corner just touches the Table 4 maximum. X5R loses a further ≈ 5–10 % at 60–85 °C, which pulls it back inside.

### 3. U_IN legs (TPS25947 SLVSFC9C) — done
| Item | Value | Result |
|---|---|---|
| R_ILM base | R137 **6.65k** to GND | 0.50 A (0.425–0.575 A, Table 6.5 test point); max allowed R_ILM |
| Leg A | R138 **3.83k** + Q11 2N7002, gate P06 USB_ILIM_1A5, R139 100k pull-down | 6.65k ∥ 3.83k = 2.43k → 1.37 A |
| Leg B | R140 **2.32k** + Q12 2N7002, gate P07 USB_ILIM_3A0, R141 100k pull-down | ∥ 2.32k = 1.19k → 2.81 A |
| Leg FET R_DS(on) | 2N7002 ≤ 7.5 Ω at 5 V, ≈ 10 Ω at 3.3 V gate | ≤ 0.4 % of 2.32k: negligible. 3.3 V gate > 2.5 V V_th max |
| OVLO | R135 1M / R136 **249k** | 1.20 × 1249/249 = **6.02 V** rising, 5.47 V falling |
| EN/UVLO | R133 1M / R134 **390k** | **4.28 V** rising, **3.88 V** falling |
| ITIMER | C67 **22 nF** | 22 nF × 1.51 V / 1.8 µA ≈ **18 ms** |
| dVdt | C66 **1.8 nF**/50 V | ≈ 1 V/ms (as E0003): inrush into ≈ 88 µF ≈ 0.09 A < 0.5 A reset limit |
| FLT | → TCA9535 P15, R90 10k up | low = at its limit (load sharing) or TSD |
| IN cap | C65 100 nF/50 V | VBUS total ≈ 1.1 µF + U2 VBUS (< 10 µF USB limit; PMID sits behind QBLK, off in HIZ) |
| AUXOFF | NC | — |
- EN/UVLO pin at a 15.4 V clamp (SMF9.0A) = 4.3 V (≤ 5 V recommended, 6.5 V abs max).
- Thermal reservation (SPEC §5.6.1) is in `docs/placement_notes.md`.

### 4. Port eFuse dividers at the corners (SPEC v1.1 §5.5) — done
- **EN/UVLO 1M / 402k 1 %** (R95/R102/R109/R116/R123, v1.1; was 365k): 1.20 × 1402/402 = **4.19 V** rising, 1.09 × 3.488 = **3.80 V** falling.
  - Corners (V_UVLO(R) 1.183–1.223 V, V_UVLO(F) 1.076–1.116 V, 1 % resistors): rising **4.08–4.33 V**, falling **3.70–3.91 V**. The lead's 4.09–4.31 / 3.72–3.93 V uses threshold tolerance only; the 1 % resistors add ±0.02 V.
  - **Rising maximum 4.33 V < battery V5 minimum 4.72 V** (4.79 V − 1.5 %): 0.39 V margin. On USB V5 ≥ 4.9 V.
  - EN pin at 5.5 V: 1.58 V (< 5 V). Divider current 3.5 µA per port (4.9 µA when the 2N7002 holds EN low).
- **TPS629210 at 3.8 V input** (SLUSEJ8: high-side R_DS(on) 250 mΩ typ; DFE252012PD-2R2M=P2 DCR 84 mΩ max, DigiKey): in 100 % mode V_OUT = V_IN − I × (R_DS(on) + DCR).
  - At 0.6 A: 0.6 × (0.25 + 0.084) = **0.20 V** drop → still regulating 3.3 V down to V5 ≈ **3.50 V**.
  - With R_DS(on) +50 % hot (375 mΩ): 0.6 × 0.459 = 0.28 V → 3.3 V held down to 3.58 V.
  - At the port UVLO falling point (3.80 V typ, 3.70 V minimum corner) the 3V3 rail stays at 3.3 V with ≥ 0.12 V to spare. The TPS629210's own UVLO (2.75 V falling) is far below. At the 0.45 A SPEC peak the margin is larger. **The MCU survives a port-UVLO event.**
- **OVLO 1M / 249k:** 6.02 V rising typ. Worst-case low: 1.183 × (0.99M + 251.5k) / 251.5k = **5.84 V** > 5.5 V (USB max), so **5.5 V never trips OVLO**. Worst-case high: 1.223 × (1.01M + 246.5k) / 246.5k = 6.23 V.
- R_ILM, ITIMER, dVdt unchanged from E0003. SMF5.0A after each eFuse (5 V stand-off, 6.4 V min breakdown: does not conduct at the 6.23 V OVLO maximum).

### 5. CC sense — done
- Rd: R129/R130 **5.1k 1 %** to GND (dead-battery safe). Sense: R131/R132 10k → GPIO6/GPIO7 (ADC1_CH5/CH6), C63/C64 1 nF at the ADC end.
- Expected CC voltage (Rp pull-up to 5 V / current source): default 0.41 V, 1.5 A 0.92–0.94 V, 3.0 A 1.68–1.69 V. Type-C sink windows (vRd): default 0.25–0.61 V, 1.5 A 0.70–1.16 V, 3.0 A 1.31–2.04 V.
- ADC/GPIO leakage: ESP32-S3 pad leakage is tens of nA (≤ 1 µA assumed): 1 µA × 10k = 10 mV shift, and it loads CC by ≤ 1 µA vs the ≥ 80 µA Rp current (≤ 1.3 % error). All levels stay ≥ 0.15 V inside their windows.
- ESP32 unpowered during the first ms after attach: the 10k limits the current into the pad's ESD diode; worst case (3 A Rp, diode at 0.5 V) CC drops to ≈ 1.39 V, still inside the 3.0 A window, and only until 3V3 is up.
- ADC range: 12 dB attenuation covers 0–3.1 V; 1 nF + 10k = 10 µs settling.

### 6. Soft power latch — done (topology per SPEC, two parts changed: D-3, D-4)
- Q13 **AO3401A** (−30 V, ±12 V, V_th −0.5 to −1.3 V, E0001/E0002 common part): S = BAT+, D → EN divider. Gate **39k to BAT+** (R148), **10k** (R149) to PL_PULL. PL_PULL ← D13 BAT54W (anode PL_PULL, cathode PB_RAW) or Q14 2N7002 (gate PWR_HOLD = GPIO36, R150 100k pull-down).
- V_GS on: −8.4 × 39/49 = **−6.7 V** at 8.4 V (< 12 V), −4.5 V at 5.6 V (S-8252 UV), well above |V_th| max 1.3 V.
- Logic: press → PB_RAW 0 V → PL_PULL ≈ 0.3 V → Q_PL on → buck on → 3V3 → firmware sets PWR_HOLD within the press (boot ≈ 0.3 s). Release: Q14 holds. Long press: GPIO21 sees PB_RAW low via D14 → firmware drops PWR_HOLD → buck off.
- **GPIO21 clamping:** PWR_BTN_N (10k to 3V3) only connects to PB_RAW through D14 (cathode at PB_RAW), so GPIO21 never sees more than 3.3 V while PB_RAW idles at up to BAT+.
- **Idle leakage:** PB_RAW floats up to ≈ BAT+ through R148 + R149 + D13 when the latch is off. Anything that sinks current from PB_RAW pulls V_GS: 0.3 V needs 7.7 µA with 39k. Sinks: D14 reverse leakage (BAT54W ≤ 2 µA at 25 V, 25 °C), D12 TPD1E10B09 (≤ 0.1 µA at 9 V), cable/switch. With SPEC's 1 MΩ gate resistor 0.3 µA would already give 0.3 V, and the PESD5V0L1UL (5 V working) would conduct at 8.4 V and turn Q_PL on: hence D-3 and D-4.
- **With USB present:** 3V3 runs from USB whatever the latch state (owner Q4). Pressing the button with USB on and no battery: see the back-feed section (c). With USB + battery, PWR_HOLD stays high (SPEC v1.1 §8.5).
- **Off drain** (latch off: no current in R148/R149, R151/R152): BQ25887 12 µA + MAX17205 ≈ 12 µA + S-8252 ≈ 6 µA + TPS56637 2 µA ≈ **32 µA** (SPEC §5.9).

### 7. DigiKey stock for every new part — done, see `bom/notes.md`
All new parts checked with pcbparts `digikey_get_part` on 2026-10-27 (one call each; E0003 parts reused without re-query). Exceptions: BQ25887RGET (T&R listing only, 211 pcs; closed: U2 changed to BQ25887RGER cut tape 296-53517-1-ND after the schematic review), 14.3k (0 stock, replaced).

### 8. ESP32-S3 pin check (changed pins) — done
| GPIO | Module pin | Net | Check |
|---|---|---|---|
| 4 | 4 | V5_SENSE | ADC1_CH3; 100k/100k + 100 nF: 2.75 V at 5.5 V (< 3.1 V range) |
| 6 | 6 | CC1_SENSE | ADC1_CH5 |
| 7 | 7 | CC2_SENSE | ADC1_CH6 |
| 36 | 29 | PWR_HOLD | free on N16R2 (quad PSRAM; only octal parts use GPIO33–37); 100k pull-down holds Q14 off during reset |
| 48 | 25 | EXP_INT_N | 3.3 V I/O on WROOM-1 (VDD_SPI 3.3 V); TCA9535 INT open drain, 10k pull-up R40 |
| 21 | 23 | PWR_BTN_N | unchanged (RTC GPIO, wake) |
- All ADC pins on ADC1 (works with Wi-Fi). Strapping GPIO0 (BOOT pull-up), GPIO3/45/46 NC as E0003. GPIO43/44 NC.
- E0003 §11 items (P50B test fit, EYESPI pin order, NTC mounting, MAX17205 tie-offs) are unchanged blocks: see E0003 notes; P50B fit in the Keystone 1121 is still an owner item.

## USB only, no battery: V5 back-feeds BAT+ (lead request, for SPEC §5)
**Path:** V5 → L1 → U17 SW → TPS56637 high-side body diode → VIN = **BAT+**. Only µA–tens of µA flow (the BAT+ loads below), so the diode drop is ≈ 0.4–0.5 V: **BAT+ ≈ V5 − 0.45 V ≈ 4.45 V at V5 4.9 V, up to ≈ 5.05 V at V5 5.5 V** (USB maximum). With no cells, BAT+ connects to C18 / C71–C73 (≈ 20 µF effective), U2 BAT, U17 VIN, Q13 source / R148, R28 → U15 VBATT, and F1 → CELL2_P → S-8252 VDD (R17 470 Ω), the reverse-cell LED string and BH2+. **MID**, **B_N** and **FET_D** float.

**(a) BQ25887 (U2)**
- **CD high (reset state, HIZ):** converter off, QBLK off, REGN off. BAT/SNS sit at ≈ 4.45–5.05 V, far inside the 12 V abs max. The QHS body diode (SW → SNS) is reverse-biased and PMID/SW are discharged, so **no pin is stressed**. BAT ≥ V_BAT_UVLO (3.7–4.42 V) may bias its I²C from BAT; the device runs from VBUS anyway. No battery detection runs in HIZ (IBAT_DISCHG only runs at converter power-up or with EN_BAT_DISCHG). The VBAT ADC reads ≈ 4.45–5.05 V. VCELL_TOP/VCELL_BOT depend on the floating MID (300 Ω to the MID net: S-8252 VC, the 100 nF caps, the LED string), so they are **undefined, but sum to VBAT**. BAT current ≤ 14 µA (IBAT spec).
- **CD low (firmware error):** the converter powers up and IBAT_DISCHG (8–16 mA) probes BAT. The body diode feeds that from V5, so BAT stays ≈ V5 − 0.6 V and **the probe can report a battery**. Charging then starts (IBAT_SHORT 100 mA or IPRECHG 150 mA, depending on the floating cell readings) into ≈ 20 µF. BAT+ ramps to **VREG 8.4 V in < 1 ms**, the current falls below ITERM, it terminates, BAT+ decays through the ≈ 50 µA loads (20 µF × 0.2 V / 50 µA ≈ 0.1 s to the recharge threshold, plus the 250 ms deglitch), and it recharges: **termination cycling, with STAT blinking** (datasheet §8.3.4: "If no battery is connected, the STAT pin blinks as capacitance connected at BAT charges, discharges, then recharges").
  - Stress: BAT+ ≤ 8.4 V (BQ25887 BAT/SNS 12 V, TPS56637 VIN 28 V, S-8252 VDD 12 V, gauge 20 V). The U17 body diode is reverse-biased at 8.4 V. A floating MID can trip cell OVP (4.37 V), which only stops charging. Auto-balancing qualifies only above 3.7 V/cell with an 80 mV split; it would move the floating MID node through 39 Ω, with no path to a supply.
  - Input draw ≤ IINDPM (500 mA default via PSEL) for microseconds per cycle. **No damage, a wrong-state symptom only**; hardware default CD = high prevents it.
- **Conclusion:** safe in both states; CD high is the hardware default.

**(b) MAX17205, S-8252AAG, protection FETs, reverse-cell LEDs**
- **MAX17205 (U15):** VBATT = BAT+ through 49.9 Ω = 4.45–5.05 V. The MAX17205 VBATT operating range is **4.2–20 V**: that figure is from distributor parametrics (Farnell / RS); analog.com did not respond from here, so recheck it in the datasheet. So the gauge is **at the bottom edge of its range: it either runs and reports the pack (VCell, stack-only) ≈ 4.45–5.05 V, or sits in POR and does not answer I²C**. Both are handled in (d). Current: tens of µA when active (SPEC uses 12 µA in hibernate; not measurable without the datasheet). CELL1/2/X = GND and CSP/CSN = SNS_P/GND carry no current.
- **S-8252AAG (U6):** VDD = CELL2_P = BAT+ via R17 470 Ω. VSS = **B_N, floating** (no cell 1). VC = MID via R18 470 Ω, also floating. Its operating current (≤ 8 µA, IOPE) flows VDD → VSS into B_N.
  - B_N can only reach GND through Q1 → FET_D → Q2 → SNS_P → R20 when Q1 is driven on, or through Q1's body diode (B_N → FET_D) when Q2 is on.
  - With VDD − VSS split over two empty "cells", each "cell" reads < 2.8 V → overdischarge → **DO low (Q1 off)**. The VM pin sits at GND through R19 2k while VSS floats up, which looks like a connected charger: with **0 V battery charge enabled (AAG)** CO can go high (Q2 on). The path is then BAT+ → R17 → U6 → B_N → Q1 body diode → Q2 → R20 → GND, and **its current is the IC's own supply current, ≤ 8 µA (IOPE max; 0.1 µA in power-down)**.
  - Otherwise B_N charges up to VDD and the IC drops below its 1.5 V operating voltage: 0 µA. The D7/D8 clamps (BAT54W) stay reverse-biased or at µA.
- **Protection FETs Q1/Q2:** at most the ≤ 8 µA above flows; V_DS ≈ 0, no stress.
- **Reverse-cell LEDs:**
  - String 2 (MID → R15 → D3 → D4 → CELL2_P) would need MID > BAT+ + ≈ 2.2 V: impossible.
  - String 1 (B_N → R16 → D5 → D6 → MID) would need B_N > MID + 2.2 V while B_N is fed only by the S-8252's µA. **No LED current (µA at most, LED dark).**
- **Total from BAT+ to GND through these parts: ≤ 8 µA (S-8252) + gauge (tens of µA)**, all supplied through the body diode from V5.

**(c) Soft latch + buck EN**
- **Latch off:** Q13 gate = source, EN = 1 µA × 53.6k = **54 mV**: buck in EN shutdown. VIN 4.45–5.05 V is **at or above the VIN UVLO wake threshold (4.0–4.4 V)**, so the IC is biased and its **SW discharge (200 Ω) is on**: this is the accepted ≈ 25 mA loss (SPEC v1.1 §13).
- **Button pressed (latch on):** EN = (BAT+ / 200k + 1 µA) / (1/200k + 1/53.6k) = **0.98 V at 4.45 V** and **1.11 V at 5.05 V** (V5 = 5.5 V, USB maximum). V_EN(ON) is 1.18 V typ, 1.26 V max; no minimum is specified (falling minimum 1.04 V).
  - At the top of the USB range a part with a low threshold **can enable**. Then V5 (held by USB at ≥ 4.9 V) is above the 4.79 V set point. D-CAP3 in Eco-mode does not switch while FB > V_REF, and pre-biased start-up waits for V_REF to exceed V_FB. **No switching, no energy transfer, and the SW discharge turns off while enabled.**
  - If USB later sagged below 4.79 V under load, the buck could only draw on the ≈ 20 µF at BAT+ (no cells): VIN collapses to its UVLO within µs. **Harmless.** Releasing the button turns it off again.
- PWR_HOLD stays low in this state (firmware, SPEC v1.1 §8.5: PWR_HOLD high only with a battery fitted).
- **Conclusion:** the buck never delivers power from the back-fed node. EN can cross only with a pressed button at the USB maximum, and that state is benign.

**(d) Firmware battery-detect window (pack 5.0–8.6 V and both BQ25887 cell readings 2.5–4.3 V)**
- **Cell criterion:** both cells ≥ 2.5 V needs VBAT = VCELL_TOP + VCELL_BOT ≥ 5.0 V. Back-feed VBAT is 4.45 V at typical USB (rejected with 0.55 V margin). It can reach **≈ 5.05 V at V5 5.5 V**, where a floating MID landing in a ≈ 50 mV band (2.50–2.55 V) would pass both cells: **margin ≈ 0 at the USB maximum**.
- **Gauge criterion:** the gauge reads the same BAT+ (4.45–5.05 V), so it **also lacks margin at the USB maximum**. If the gauge is in POR (≤ 4.2 V region), firmware uses the BQ25887 fallback (SPEC §8.11), which has the same VBAT.
- **Recommendation (firmware only, no hardware change), for SPEC §8.4:**
  1. Auto-enable charging only for **pack ≥ 5.6 V** (= S-8252 UV 2.8 V/cell; a real pack above it is unambiguous: 0.55 V above the back-feed maximum).
  2. Packs reading 5.0–5.6 V (deeply discharged, or back-feed) get a **precharge probe** first. Firmware sets IPRECHG 150 mA with IINDPM ≤ the source budget, drives CD low for ≈ 50 ms, then reads VBAT.
     - **No battery:** ≈ 20 µF charges at 150 mA (7.5 V/ms), so VBAT jumps to VREG 8.4 V within ≈ 1 ms. Firmware sees **VBAT > 6.5 V from a < 5.6 V start → no battery → CD high**.
     - **Real pack:** VBAT rises by millivolts, which is the correct precharge for a deep pack.
     - The BQ25887 balancing FETs cannot do this test: balancing only qualifies above 3.7 V/cell.
  3. Diagnostic only: with the buck off, back-feed shows as **VBAT ≈ V5 − (0.3–0.6 V)** (V5 = 2 × V5_SENSE).
- **Hardware alternative (not fitted, single passive, tell-before-fit):** 1 MΩ from MID to GND makes a cell-less MID read 0 V, so it is deterministically rejected. Cost: one RC0402FR-071ML (common). **Side effect: a permanent 3.5–4.2 µA drain on the bottom cell only** (≈ 35 mAh/year imbalance, absorbed by balancing, but it adds ≈ 4 µA to the 32 µA off drain). I recommend the firmware test instead.

**(e) Extra draw from V5 in USB-only / no battery** (on top of the normal 3V3 / port load)
| Item | Path | Current from V5 | Source |
|---|---|---|---|
| TPS56637 SW discharge | V5 → L1 → SW → 200 Ω → GND | **≈ 24.5 mA** at V5 4.9 V (122 mW; 27.5 mA at 5.5 V) | R_DISCHG 200 Ω typ at 25 °C (§6.5); not specified hot or continuous |
| TPS56637 VIN bias (EN low, discharge FET on) | body diode → VIN | ≈ 2 µA spec (I_SD at V_EN = 0), unspecified with the discharge FET biased: assume ≤ 0.1 mA | SLVSEG1A §6.5 |
| BQ25887 BAT (HIZ) | body diode → BAT | ≤ 14 µA | IBAT |
| MAX17205 VBATT | body diode → R28 | tens of µA when active, ≈ 0 in POR | see (b) |
| S-8252AAG | R17 → VDD → B_N → Q1/Q2 → GND | ≤ 8 µA | IOPE |
| Latch / EN divider | R148, R151/R152 | 0 with the latch off (18 µA + 91 µA only while the button is held) | — |
| PB_RAW leakage (D14 reverse, D12) | R148/R149/D13 | ≤ 2 µA | BAT54W, TPD1E10B09 |
| **Total back-feed + discharge** | | **≈ 24.6 mA (≈ 0.12 W)**, 99.6 % of it the SW discharge | |
| (always present with any source) V5_SENSE 100k/100k + 5 × port OVLO (1M/249k) + 5 × port EN (1M/402k, or 1M when held off) | dividers | ≈ 24.5 + 19.6 + 17.5–24.5 ≈ **62–69 µA** | not specific to this state |

**Result: nothing misbehaves.** The back-feed is accepted as the known ≈ 25 mA loss (SPEC v1.1 §13), with three firmware notes for SPEC §8:
1. Keep CD high without a detected battery (already §8.4).
2. Raise the auto-charge threshold to a 5.6 V pack, and gate 5.0–5.6 V on the precharge probe ((d)).
3. Keep PWR_HOLD low without a battery (§8.5).

The only hardware option worth noting is the 1 MΩ MID pull-down in (d). It is not fitted.

## Deviations from SPEC (datasheet- or stock-driven) — D-1 to D-5 accepted by the lead (SPEC v1.1)
| # | SPEC | Schematic | Why |
|---|---|---|---|
| D-1 | SNS 2 × 22 µF ≥ 16 V | **2 × 47 µF/16 V 1210** (CL32A476KOJNNNE) | No common 22 µF ≥ 16 V part; 47 µF 1210 is the V5 bulk part, ≈ 45 µF effective at 8.4 V ≥ datasheet's 44 µF |
| D-2 | FB "100k / 14.3k class" | **69.8k / 10.0k** (4.788 V) | RC0402FR-0714K3L 0 stock; 10.0k is Table 4's R7 and a common part |
| D-3 | Q_PL gate pulled to BAT+ by **1 MΩ** | **39 kΩ** (common RC0402FR-0739KL) | Leakage on PB_RAW (D14 reverse, ESD) would turn Q_PL on through 1 MΩ; 39k needs 7.7 µA for 0.3 V. No extra off-state drain (gate = source when off) |
| D-4 | J12 ESD **PESD5V0L1UL** (as E0003) | **TPD1E10B09DPYR** (9 V, bidirectional, 0402) | PB_RAW idles at up to 8.4 V via the latch; a 5 V TVS would conduct and switch the latch on |
| D-5 | SPEC §10 planned "U4 TPS56637" | **U17** (U_IN = U16) | U4 is the USBLC6 in E0003; references kept |
| D-6 | — | Firmware rule: **PWR_HOLD high while USB is attached and a battery is fitted** | **Adopted in SPEC v1.1 §8.5** (SW discharge, §13) |

## Liberties taken
- **L-1:** TPS56637 feed-forward R155 20k + C79 100 pF (now in SPEC v1.1 §5.7; 100 pF chosen per the datasheet design, see checklist 2).
- **L-2:** 3V3 input cap C22 changed 4.7 µF → 10 µF/25 V and the port eFuse input caps 100 nF → 10 µF/25 V (SPEC §5.1.1 bulk list), same references.
- **L-3:** TPD1E10B09 footprint: KiCad `Diode_SMD:D_0402_1005Metric` for TI's X1SON-2 (DPY, 1.0 × 0.6 mm): **check pads against TI's DPY land pattern before layout** (Router).
- **L-4:** PMID 2 × 10 µF/25 V (SPEC "10 µF"; the datasheet recommends ≥ 10 µF after derating).
- **L-5:** CHG_PSEL is a global label (forced) only so the U2 pin column looks clean; electrically local.
- **L-6:** GPIO37 → EYESPI GP1 DNP 0R uses E0003's R60 (was GPIO36 → GP1); GP2 left NC (SPEC §5.11).

## Open items
- **O-1** closed (SPEC v1.1): L1 3.3 µH, V5 ≈ 85–88 µF effective, inside Table 4. Bench load step 0.5 → 4 A on battery remains a normal bring-up check (FF C79 100 → 220 pF if it rings).
- **O-2** closed as **SPEC v1.1 §8.5, §13**. **O-2b (bench):** TPS56637 temperature in USB-only / no-battery with the ≈ 25 mA SW discharge running.
- **O-6** firmware battery-detect margin at USB 5.5 V (back-feed section (d)): proposed §8.4 change (5.6 V auto-charge threshold + precharge probe), for the lead.
- **O-3** BQ25887 sourcing: DigiKey lookup returns the RGET T&R listing only (211 pcs, MOQ 250). Buy BQ25887RGER cut tape (SPEC: 10 911 on reel) or confirm RGET cut tape at order time.
- **O-4** USB-unplug dip at full load (SPEC §5.1.1) and U_IN temperature at 2.81 A (SPEC §5.6.1, fallback leg B 2.94k): bench.
- **O-5** E0003 open items carried over: P50B fit in the 1121 (owner sample), SM04B/SM02B-GHS-TB from LCSC (DigiKey 0 stock on 2026-10-18).
