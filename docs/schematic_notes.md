# E0005 schematic capture notes (Phase 2, 2026-10-27)

**Spec:** `docs/SPEC.md` **v1.0 (frozen)**. Reference design: E0003 (copied, not edited).

**Root:** `E0005_controller.kicad_sch`, 4 hierarchical sheets, 273 symbols (272 BOM parts + net tie NT1):

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
- `build/scripts/check_fp.py`: all 273 footprints exist; pin numbers = pad numbers for all 39 symbol/footprint pairs.
- `build/scripts/check_refs.py`: every reference shared with E0003 is the same part, except the intended changes listed below.
- `build/scripts/make_bom.py` writes `bom/E0005_digikey_bom.csv` from the schematic fields.
- Net-by-net audit done from the netlist for every new circuit (U_IN, legs, charger, buck, latch, CC, V5_SENSE, TCA9535 map, ESP32 pins).

## Reference designators
E0003 references are kept for every part that stays (same generation order; removed parts leave their numbers unused). New parts are numbered above E0003's highest: R129–R155, C63–C79, Q11–Q14, U16, U17, L2.
- **Same ref, changed part (role unchanged):** U2 BQ25798 → **BQ25887**; D1 TVS2200 → **SMF9.0A**; D12 PESD5V0L1UL → **TPD1E10B09** (see D-4, L-3); D13 (was QON diode) → latch diode; D19/21/23/25/27 SMF9.0A → **SMF5.0A**; port dividers R95/R102/R109/R116/R123 232k → **365k**, R97/R104/R111/R118/R125 137k → **249k**; C48/51/54/57/60 100 nF → **10 µF/25 V** (SPEC §5.1.1); C22 4.7 µF → **10 µF/25 V** (3V3 input, SPEC §5.1.1); L1 SRP7028A-2R2M is now the 5 V buck inductor; R60 DNP 0R now GPIO37 → GP1.
- **Removed:** U3 STUSB4500, U7 BQ29209, Q8–Q10, the BQ25798 support parts, MID divider (R33/R34/C34), PD_ALERT_N pull-up R39, GP2 option R61, P06 pull-up R91.
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

### 2. TPS56637 FB and EN dividers, caps — done (two items open, O-1/O-2)
- **FB:** R153 **69.8k** / R154 **10.0k** (1 %): V_OUT = 0.6 × (1 + 6.98) = **4.788 V** (−0.25 % vs 4.80 V). V_FB ±1.5 % over temperature → 4.72–4.86 V, inside SPEC D1 (4.70–5.25 V). (SPEC "100k / 14.3k class": 14.3k RC0402FR-0714K3L has **0 stock**; 69.8k/10k is datasheet Table 4's R7 = 10k form; see deviation D-2.)
- **Feed-forward:** R155 20k + C79 100 pF across R153 (Table 4, 5 V row: R8 20k, C9 100–220 pF; TI EVM Fig. 17 fits them). Fitted; tune at bring-up (O-1).
- **EN UVLO** (SLVSEG1A §7.3.4, Ip 1 µA, Ih 4 µA, V_EN rising 1.18 V typ / 1.26 V max, falling 1.12 V typ / 1.04 V min): R151 **200k** (from Q_PL drain) / R152 **53.6k** to GND.
  - Start: 1.18 + 200k × (1.18 / 53.6k − 1 µA) = **5.38 V** typ (**5.76 V** at V_EN 1.26 V).
  - Stop: 1.12 + 200k × (1.12 / 53.6k − 5 µA) = **4.30 V** typ: 1.08 V hysteresis (> 0.5 V recommended).
  - EN at 8.4 V, running: (8.4 / 200k + 5 µA) / (1/200k + 1/53.6k) = **1.99 V** (≤ 5.5 V recommended, 6 V abs max).
  - Back-feed (BAT+ ≈ 4.3 V, button pressed): EN = (4.3/200k + 1 µA) / (1/200k + 1/53.6k) = **0.95 V** < V_EN(ON): stays off.
  - Latch off: EN = 1 µA × 53.6k = 54 mV.
  - Divider current when on: 8.4 V / 254k = 33 µA; zero when the latch is off.
- **MODE → GND** (≤ 10 kΩ) → Eco-mode: no negative inductor current, so the buck never sinks from V5 when USB holds V5 above 4.79 V.
- **PG** → TCA9535 P17, 10k to 3V3 (< 5.5 V). PG is low whenever EN is low with VIN present (Table 2): firmware reads it only while the buck is meant to run.
- **Caps:** VIN 2 × 10 µF/25 V + 100 nF (C71–C73, ≥ 8.4 V rating); BOOT C74 100 nF/50 V (≥ 10 V, X7R); output **4 × 47 µF/16 V 1210 at the buck** (C75–C78) + **2 × 47 µF at the ports** (C61/C62) + 10 µF/25 V at the 5 port eFuses and the 3V3 input = SPEC §5.1.1's 282 µF nominal / ≈ 200 µF effective.
- **Inductor:** L1 SRP7028A-2R2M (SPEC). Ripple at 8.4 V in: 4.8 × 3.6 / (8.4 × 2.2 µH × 500 kHz) = 1.87 A p-p; peak at 6 A = 6.9 A ≪ 14 A Isat.
- **O-1 (open, bench):** Table 4 recommends 3.3 µH and C_OUT 20–100 µF *effective* for 5 V. SPEC keeps 2.2 µH (fast ramp for the USB-unplug dip, §5.1.1) and ≈ 200 µF effective on V5. LC double pole 1/(2π√(2.2 µH × 200 µF)) ≈ 7.6 kHz vs ≈ 8.8 kHz for Table 4's 3.3 µH / 100 µF corner (15 % lower). The feed-forward network is fitted for phase margin. Bench: load-step 0.5 → 4 A on battery, check ringing; fallbacks, all resistor/cap changes: C79 220 pF, or fit 2 of the 4 buck-side 47 µF only.
- **O-2 (open, firmware + bench):** the SW discharge MOSFET (200 Ω, §7.3.9) turns on whenever the TPS56637 is shut down by EN with VIN present. With **USB on and the latch off**, V5 (≈ 5 V from USB) → L1 → SW → 200 Ω → GND: **≈ 25 mA, 125 mW** from USB. Firmware rule (added for SPEC §8): with USB attached and a battery fitted, keep PWR_HOLD high (the buck idles in Eco-mode at ≈ 140 µA because USB holds V5 above its set point, and the board load-shares as SPEC §5.1 intends). Residual case: **USB only, no battery**: BAT+ back-fed ≈ 4.3 V may power the IC (VIN UVLO wake 4.0–4.4 V) with EN low → the same 25 mA drain from USB. Functionally harmless (it is USB power); the continuous rating of the discharge FET is not specified: check the TPS56637 temperature on the bench. Hardware fix if needed: none with resistor changes only; would need a different buck or an output switch (lead decision).
- **OVP:** 125 % of V_FB = 5.99 V on V5. With USB at 5.5 V V5 ≤ 5.5 V (114.6 %, just below the 115 % PG upper threshold). Only a faulty source between 5.99 V and U_IN OVLO (5.85–6.25 V) can trip it (non-latched, 25 ms hiccup).

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
| dVdt | C66 **1.8 nF**/50 V | ≈ 1 V/ms (as E0003): inrush into ≈ 200 µF ≈ 0.2 A < 0.5 A reset limit |
| FLT | → TCA9535 P15, R90 10k up | low = at its limit (load sharing) or TSD |
| IN cap | C65 100 nF/50 V | VBUS total ≈ 1.1 µF + U2 VBUS (< 10 µF USB limit; PMID sits behind QBLK, off in HIZ) |
| AUXOFF | NC | — |
- EN/UVLO pin at a 15.4 V clamp (SMF9.0A) = 4.3 V (≤ 5 V recommended, 6.5 V abs max).
- Thermal reservation (SPEC §5.6.1) is in `docs/placement_notes.md`.

### 4. Port eFuse dividers at the corners — done
- EN/UVLO 1M / **365k**: 1.20 × 1365/365 = **4.49 V** rising, 1.09 × 3.74 = **4.08 V** falling.
  Worst-case rising (V_UVLO(R) 1.223 V, 1 % resistors): 1.223 × (1.01M + 361.4k) / 361.4k = **4.64 V** < battery V5 minimum 4.79 V − 1.5 % = **4.72 V** (margin 80 mV; with the typical 4.49 V, 230 mV). On USB V5 ≥ 4.9 V.
- OVLO 1M / **249k**: 6.02 V rising typ. Worst-case low: 1.183 × (0.99M + 251.5k) / 251.5k = **5.84 V** > 5.5 V (USB max): **5.5 V never trips OVLO**. Worst-case high: 1.223 × (1.01M + 246.5k) / 246.5k = 6.23 V (SPEC 6.25 V).
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
- **Idle leakage:** PB_RAW floats up to ≈ BAT+ through R148 + R149 + D13 when the latch is off. Anything that sinks current from PB_RAW pulls V_GS: 0.3 V needs 7.7 µA with 39k. Sinks: D14 reverse leakage (BAT54W ≤ 2 µA at 25 V, 25 °C), D12 TPD1E10B09 (≤ 0.1 µA at 9 V), cable/switch. With SPEC's 1 MΩ gate resistor 0.3 µA would already give 0.3 V, and the PESD5V0L1UL (5 V working) would conduct at 8.4 V and turn Q_PL on: hence D-3 and L-3.
- **With USB present:** 3V3 runs from USB whatever the latch state (owner Q4). Pressing the button with USB on and no battery: Q_PL passes ≈ 4.3 V, EN 0.95 V → buck stays off. See O-2 for PWR_HOLD with USB + battery.
- **Off drain** (latch off: no current in R148/R149, R151/R152): BQ25887 12 µA + MAX17205 ≈ 12 µA + S-8252 ≈ 6 µA + TPS56637 2 µA ≈ **32 µA** (SPEC §5.9).

### 7. DigiKey stock for every new part — done, see `bom/notes.md`
All new parts checked with pcbparts `digikey_get_part` on 2026-10-27 (one call each; E0003 parts reused without re-query). Exceptions: BQ25887RGET (T&R listing only, 211 pcs), 14.3k (0 stock, replaced).

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

## Deviations from SPEC v1.0 (datasheet- or stock-driven)
| # | SPEC | Schematic | Why |
|---|---|---|---|
| D-1 | SNS 2 × 22 µF ≥ 16 V | **2 × 47 µF/16 V 1210** (CL32A476KOJNNNE) | No common 22 µF ≥ 16 V part; 47 µF 1210 is the V5 bulk part, ≈ 45 µF effective at 8.4 V ≥ datasheet's 44 µF |
| D-2 | FB "100k / 14.3k class" | **69.8k / 10.0k** (4.788 V) | RC0402FR-0714K3L 0 stock; 10.0k is Table 4's R7 and a common part |
| D-3 | Q_PL gate pulled to BAT+ by **1 MΩ** | **39 kΩ** (common RC0402FR-0739KL) | Leakage on PB_RAW (D14 reverse, ESD) would turn Q_PL on through 1 MΩ; 39k needs 7.7 µA for 0.3 V. No extra off-state drain (gate = source when off) |
| D-4 | J12 ESD **PESD5V0L1UL** (as E0003) | **TPD1E10B09DPYR** (9 V, bidirectional, 0402) | PB_RAW idles at up to 8.4 V via the latch; a 5 V TVS would conduct and switch the latch on |
| D-5 | SPEC §10 planned "U4 TPS56637" | **U17** (U_IN = U16) | U4 is the USBLC6 in E0003; references kept |
| D-6 | — (SPEC §5.7 "PG pull-up", §8) | Firmware rule: **PWR_HOLD high while USB is attached and a battery is fitted** | TPS56637 SW discharge (200 Ω) is on whenever EN is low (O-2); please add to SPEC §8 |

## Liberties taken
- **L-1:** TPS56637 feed-forward R155 20k + C79 100 pF fitted (datasheet Table 4 / EVM), not in SPEC.
- **L-2:** 3V3 input cap C22 changed 4.7 µF → 10 µF/25 V and the port eFuse input caps 100 nF → 10 µF/25 V (SPEC §5.1.1 bulk list), same references.
- **L-3:** TPD1E10B09 footprint: KiCad `Diode_SMD:D_0402_1005Metric` for TI's X1SON-2 (DPY, 1.0 × 0.6 mm): **check pads against TI's DPY land pattern before layout** (Router).
- **L-4:** PMID 2 × 10 µF/25 V (SPEC "10 µF"; the datasheet recommends ≥ 10 µF after derating).
- **L-5:** CHG_PSEL is a global label (forced) only so the U2 pin column looks clean; electrically local.
- **L-6:** GPIO37 → EYESPI GP1 DNP 0R uses E0003's R60 (was GPIO36 → GP1); GP2 left NC (SPEC §5.11).

## Open items
- **O-1** TPS56637 L/C vs Table 4 (bench load step, FF tuning).
- **O-2** TPS56637 SW discharge with EN low and V5 held by USB (firmware rule D-6; bench temperature in USB-only, no-battery state).
- **O-3** BQ25887 sourcing: DigiKey lookup returns the RGET T&R listing only (211 pcs, MOQ 250). Buy BQ25887RGER cut tape (SPEC: 10 911 on reel) or confirm RGET cut tape at order time.
- **O-4** USB-unplug dip at full load (SPEC §5.1.1) and U_IN temperature at 2.81 A (SPEC §5.6.1, fallback leg B 2.94k): bench.
- **O-5** E0003 open items carried over: P50B fit in the 1121 (owner sample), SM04B/SM02B-GHS-TB from LCSC (DigiKey 0 stock on 2026-10-18).
