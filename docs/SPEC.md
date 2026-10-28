# E0005 — ESP32-S3 5 V controller board: Hardware Requirements & Architecture Spec

| | |
|---|---|
| Status | **v1.4 — FROZEN; E0005 rev A COMPLETE (2026-10-28).** Spec → schematic → placement → routing → fab outputs, all approved by PlaceRoute. Fab package `fab/E0005_revA/` (approved), routing final at `50c434e`. Before ordering: `fab/E0005_revA/PREORDER.md`. |
| Date | 2026-10-27 (v0.1 – v1.2), 2026-10-28 (v1.3, v1.4) |
| Scope | **PCB only.** Enclosure and firmware are out of scope; §8 lists only the firmware rules the hardware relies on. |
| Reference design | **E0003** (`../E0003 - ESP32 control box mainboard`, spec v1.5, order-ready). E0005 reuses its MCU, battery, protection, gauge, I²C, LCD, switch and button blocks, its footprints/libraries and its DigiKey parts. **Only what "5 V only" forces is changed** (§1.1). |
| Sister designs | E0001 (fader driver, 4 per box) and E0002 (haptic knob, 1 per box) are **not part of this job**. E0005 keeps their connectors and pinouts with **+5 V** on the power pins. **E0001 rev C and E0002 rev B need 6–9 V (PBUS) and will not work on E0005; 5 V revisions are needed later (out of scope).** §6 is the host-interface spec they will need. |
| Build | 4-layer, DigiKey-preferred BOM, hand assembly with a stencil. **No test points.** |

### Revision history
| Rev | Change |
|---|---|
| v0.1 | First draft from the lead brief (owner option A: plain 5 V USB, no PD) and E0003 v1.5 |
| v0.2 | PlaceRoute review: (1) **U_IN limit in three levels, 0.50 A at reset** / 1.37 A / 2.81 A, two FET legs on TCA9535 P06/P07; **VBUS budget rule** (U_IN + charger IINDPM ≤ source) in §8.3. (2) U_IN behaviour after ITIMER confirmed from TPS25947 SLVSFC9C §7.3.5.3, §7.3.8 and Table 7-3, §5.1 and §5.2 made consistent. (3) U_IN thermal check, copper reservation (§5.6.1). (4) V5 bulk and USB-unplug dip (§5.1.1); V5 bulk raised to 6 × 47 µF. (5) BQ25887 per-cell ADC as the fallback battery-level source (§8.11). FLT of U_IN is low during normal load sharing (§8.9). |
| **v1.0** | **Owner answers (all as recommended), spec frozen:** Q1 keep the **MAX17205** gauge; Q2 **drop the BQ29209**; Q3 keep E0003's port limits (**E0001 ≤ 0.6 A, E0002 ≤ 2.0 A, firmware budget 4.4 A**); Q4 **"off" with USB plugged in = board stays on from USB and charges**; Q5 private GitHub repo `Karpuls/E0005-esp32-s3-5v-controller`, pushed at every milestone. |
| **v1.1** | Schematic-review corrections (lead, from the Phase 2 checks): (1) **TPS56637 output filter inside datasheet Table 4 (SLVSEG1A, 5 V row): L 3.3 µH, V5 effective C ≤ 100 µF** (v1.0 had 2.2 µH and ≈ 200 µF): V5 bulk is now 2 × 47 µF + the 10 µF eFuse/3V3 input caps ≈ 85–95 µF effective. (2) **Port eFuse UVLO 1 M / 402 k → 4.19 V rising / 3.80 V falling** (was 4.49/4.08 V), to keep the USB-unplug dip margin with the smaller C (§5.1.1, recomputed). (3) **Low-pack derating rule** §8.6: V5 load ≤ 3.0 A below a 6.8 V pack. (4) **PWR_HOLD rule** §8.5: TPS56637's 200 Ω SW discharge (datasheet §7.3.9) is on whenever EN is low, drawing ≈ 25 mA from USB, so PWR_HOLD stays high while USB is attached and a battery is fitted; ≈ 25 mA remains in USB-only/no-battery (buck VIN back-fed, §13). (5) Schematic deviations D-1…D-5 accepted (`docs/schematic_notes.md`). TPS56637 OVP at 125 % ≈ 6.0 V is above USB's 5.5 V max on V5. |
| **v1.2** | PlaceRoute item: **USB-only/no-battery back-feed** of V5 into BAT+ through the TPS56637 high-side body diode, analysed (§5.1.2, `docs/schematic_notes.md`): nothing misbehaves. **§8.4 battery detect tightened:** auto-charge only for a pack ≥ 5.6 V; 5.0–5.6 V only after a precharge probe. The 1 MΩ MID pull-down alternative was not fitted. |
| **v1.3** | **Outline 125 × 73 mm** (was ≈ 125 × 65), owner decision via PlaceRoute (no strict size limit; enlarge where it helps routing). +8 mm at the **north** edge: the J1–J5 port band (connectors, eFuses U10–U14 with their parts) and the U16 USB-input stage moved north with the edge, because the band between U8/U9 and the port eFuses was full on all routing layers. Everything else (BH1/BH2, U1, antenna keep-out) stayed put. 4 × M3 holes keep the 4 mm corner inset (`E0005_board:Holes_4xM3_125x73`), R3 corners. Details in `docs/routing_notes.md`. |
| **v1.4** | **Routing copper sizing (PlaceRoute decision):** copper is sized for a **4.6 A design current on V5** and **5 A on the pack path** at **ΔT ≤ 20 °C** (IPC-2152). The 4.4 A firmware port budget is unchanged; short-term peaks up to the 4.85 A worst plausible V5 load are accepted (≈ 22 °C). The buck current limit and F1 stay the hardware backstops above that. |
| **rev A done** | 2026-10-28: Phase 5 (fab outputs) complete and approved by PlaceRoute. No spec change. |

---

## 1. Summary of the architecture

| Function | Decision | Why, in one line |
|---|---|---|
| MCU | **ESP32-S3-WROOM-1-N16R2** (as E0003) | Native USB (flash, CDC, JTAG), 2 × I²C, 2 MB PSRAM for the LCD buffer, Wi-Fi/BLE |
| Battery | **2 × Molicel P50B 21700, 2S1P, 2 × Keystone 1121 on the bottom** (as E0003) | 36 Wh; PCB makes the series link and the mid-point tap |
| USB-C | **5 V only, no PD**: 2 × 5.1 kΩ Rd, CC1/CC2 → ESP32 ADC for the Rp current level (default / 1.5 A / 3.0 A) | Owner option A; the board knows how much the source can give without a PD controller |
| USB input | **TPS259470A eFuse** (OVLO 6.0 V, reverse blocking, I_LIM **0.50 A** at reset, **1.37 A** or **2.81 A** selected by firmware) → 5 V system rail **V5** | USB feeds the system directly (power path); the battery buck can never back-feed VBUS |
| Charger | **TI BQ25887** 2 A boost charger 5 V → 2S, I²C, 16-bit ADC (VBUS, IBUS, per-cell voltages, TS), **integrated cell balancing**, cell OVP, JEITA | DigiKey-stocked TI part made for "5 V USB → 2S"; replaces BQ25798 + STUSB4500 (+ BQ29209, see §5.4) |
| Battery → 5 V | **TI TPS56637** 6 A sync buck (Eco-mode), BAT → V5 at **4.80 V**, EN from a soft power latch | Supplies V5 with no USB, and **tops up V5 automatically when the load exceeds the USB limit** |
| 5 V system rail | **V5 = diode-OR of USB (eFuse, ≈ 4.9–5.1 V) and the buck (4.80 V)**, sized for **6 A** | One protected rail feeds the 3V3 buck and every port (owner option A) |
| 3V3 | **TPS629210** 1 A buck from V5 (as E0003, now from V5) | A port fault never resets the MCU |
| Pack protection | **S-8252AAG** + 2 × **PSMN2R0-30YLDX** + **10 A fuse F1** (as E0003) | Hardware-only OV/UV/short; works with no firmware |
| Battery level (measured by the ESP32) | **MAX17205** fuel gauge, stack-only, 5 mΩ sense (as E0003) + BQ25887 per-cell ADC | SoC %, remaining time, pack voltage/current; per-cell voltages from the charger ADC |
| Ports | 4 × E0001 (JST-GH 4p) + 1 × E0002 (JST-GH 6p), **+5 V**, one **TPS259470A** eFuse each (OVLO 6.0 V, UVLO 3.8 V, I_LIM as E0003), PCA9548A mux | Same blocks as E0003 with 5 V thresholds |
| LCD | **Adafruit 4311** on EYESPI J10 (as E0003) | |
| Switches | 4 × JST-GH 2p, pull-up + RC + ESD (as E0003) | |
| On/off | Power button → **soft power latch on the buck EN** + GPIO21; BOOT, RESET (as E0003, latch new) | "Off" = buck off, ≈ 35 µA drain; no ship-mode charger needed |
| Outline | **125 × 73 mm** (v1.3; E0003's 125 × 65 + 8 mm north), 4 × M3, E0003 edge plan (§9) | No size limit; reuses the reviewed holder and antenna placement; extra room for the port band |

### 1.1 What changes against E0003
| E0003 block | E0005 | Reason |
|---|---|---|
| STUSB4500 PD sink | **removed**; CC Rd + ADC Rp detection | No PD (option A) |
| BQ25798 buck-boost NVDC charger, VSYS = PBUS 6–9 V | **BQ25887** boost charger (5 V → 2S), no system output | 5 V input only; the system no longer runs from a 2S rail |
| — | **TPS56637** 2S → 5 V buck + **USB input eFuse** (6th TPS259470A) | New 5 V system rail V5 |
| TVS2200DRVR on VBUS (BOM exception, LCSC) | **SMF9.0A** (already a common part) | VBUS is 5 V now; clamps 15.4 V < 20 V BQ25887 abs max; BOM exception gone |
| BQ29209 balancer + secondary OV, Q10/BAL_EN, OV2 FET | **removed** (owner Q2, v1.0) | BQ25887 balances (≈ 110 mA, measured with charge paused) and has its own cell OVP |
| Port eFuses OVLO 10 V / UVLO 5.8 V, SMF9.0A port TVS | OVLO **6.0 V** / UVLO **3.8 V**, **SMF5.0A** port TVS | 5 V ports |
| Silkscreen "PBUS 6–9 V" | **"5V"** + port number + "E0001"/"E0002" | Brief |
| MID → ESP32 GPIO4 divider | **removed**; GPIO4 = **V5_SENSE** | BQ25887 ADC gives both cell voltages |
| 3V3 buck from VSYS | from **V5** | |
| BQ25798 QON ship mode | buck-EN soft power latch | BQ25887 has no ship mode / BATFET |
| O-1 open risk (no SFET) | **closed**: no BATFET in the path; the buck's current limit (6.3–8.6 A valley) bounds the system's battery draw | |

---

## 2. Requirements

### 2.1 Functional (owner)
| ID | Requirement |
|---|---|
| R1 | 4-layer board, **ESP32-S3-WROOM-1-N16R2**. |
| R2 | **2 × Molicel P50B in series (2S)**; the **battery level is measured by the ESP32**. |
| R3 | **USB(-C)** for programming (native USB) and charging. **Runs from USB with no battery fitted.** |
| R4 | **5 V only (option A):** plain 5 V USB, **no PD**. One protected **5 V system rail** feeds the 3V3 regulator and every port. USB in → V5 from USB (power path); battery only → V5 from a 2S → 5 V buck. The pack is charged from 5 V USB by a boost charger. |
| R5 | Connectors: 1 × EYESPI display (Adafruit 4311), 4 × switch inputs, **4 × E0001 ports**, **1 × E0002 port**. |
| R6 | No strict size limit. |
| R7 | E0001 (GH4: 1 +5V, 2 SCL, 3 SDA, 4 GND) and E0002 (GH6: 1–2 +5V, 3 SCL, 4 SDA, 5–6 GND) pinouts unchanged, **+5 V** on the power pins, silkscreen **"5V"** at each port. |
| R8 | House rules: no test points; no vias on/under pads (≥ 0.15 mm via-to-pad copper; EP thermal vias exempt); tracks at multiples of 45°; DigiKey-preferred BOM with common parts as defaults; JLC 4-layer impedance stackup (90 Ω USB pair); JLC rules + no-via-on-pad rule in `.kicad_dru`. |

### 2.2 Derived requirements
| ID | Requirement |
|---|---|
| D1 | V5 at every port stays within **4.70–5.25 V** at the host connector in all normal states (USB, battery, both, charging). |
| D2 | V5 never exceeds **≈ 6.2 V at a port** (eFuse OVLO), even with a faulty USB source up to 20 V. |
| D3 | Port current limits as E0003: GH4 ≤ 1.0 A incl. tolerance, GH6 2.0 A nominal. |
| D4 | The MCU keeps running when any port is shorted or the USB source is overloaded. |
| D5 | No current from the battery buck into VBUS or the USB host, ever. |
| D6 | Charge/discharge inside the P50B ratings (charge ≤ 2.2 A used vs 5 A standard; discharge ≤ 9 A vs 60 A). |
| D7 | Antenna keep-out as E0003 (≥ 15 mm to the cans). |

### 2.3 Not on this board
Firmware · enclosure · USB-PD · USB OTG/source · 5 V revisions of E0001/E0002 · detection or protection against plugging the 6–9 V E0001 rev C / E0002 rev B in (silkscreen only, as E0003's owner decision) · UART header · SD card (on the LCD module).

---

## 3. Block diagram

```
 USB-C J11 ═╦═ VBUS 5 V ─► SMF9.0A ─┬─► BQ25887 VBUS (charger, I2C0 0x6A, CD ← expander, default OFF)
            ║                       │       boost 1.5 MHz, 1 µH ──► BAT+ ── F1 10 A ── Cell 2 (+)
            ║  CC1/CC2 ─ 5.1k Rd ─► ESP32 ADC (GPIO6/7): Rp level 0.5 / 1.5 / 3.0 A        │
            ║  D+/D−  ─► USBLC6 ─► ESP32-S3 GPIO19/20 (native USB)                       MID ─┤ P50B ×2
            ▼                       │                                     (BQ25887 MID/CBSET, │ S-8252 VC)
                                    ▼                                                        │
                     U_IN TPS259470A eFuse                       Cell 1 (−) = B− ─ Q_DSG ║ Q_CHG ─ R_SENSE 5 mΩ ─ GND
                     OVLO 6.0 V, reverse blocking,                     S-8252AAG OV/UV/OC/SC · MAX17205 gauge (0x36)
                     I_LIM 0.50 / 1.37 / 2.81 A                                              │
                                    │  ≈ 4.9–5.1 V                                   BAT+ ───┤
                                    ▼                                                        ▼
        ╔══════════════════  V5 (5 V system rail, 6 A)  ◄══════════  TPS56637 buck, BAT → 4.80 V, Eco-mode
        ║                                                             EN ← soft power latch (PWR button / PWR_HOLD)
        ╠═► TPS629210 ─► +3V3: ESP32-S3, PCA9548A, TCA9535, LCD, pull-ups
        ╠═► V5_SENSE divider ─► GPIO4
        ║
        ├────────┬────────┬────────┬────────┐   each: TPS259470A, OVLO 6.0 V, UVLO 3.8 V, EN ← expander (off at reset)
     eFuse1   eFuse2   eFuse3   eFuse4   eFuse5
     ≤1.00 A  ≤1.00 A  ≤1.00 A  ≤1.00 A  2.0 A nom
     J1 GH4   J2 GH4   J3 GH4   J4 GH4   J5 GH6        silkscreen "5V" + port + E0001/E0002
        ▲        ▲        ▲        ▲        ▲          SCL/SDA: 4.7 k to 3V3, ESD, 220 Ω series
        └ch0─────┴ch1─────┴ch2─────┴ch3─────┴ch4── PCA9548A (0x70) ◄── I2C1 ◄── ESP32-S3
                                                ch5 ── EYESPI SCL/SDA
   ESP32-S3 ─ FSPI + DC/RST + LITE ─► J10 EYESPI ─► Adafruit 4311     ESP32 ◄─ SW1..SW4 (J6..J9)
```

---

## 4. MCU — ESP32-S3-WROOM-1-N16R2 [as E0003]
Unchanged from E0003 §4: native USB-Serial/JTAG on GPIO19/20 (no UART pads), FSPI on IO_MUX pins for the LCD, two I²C controllers, RTC GPIOs for switches and the power button, Wi-Fi + BLE with the antenna at the east edge. Quad PSRAM, so GPIO35–37 are free. Pin map in §7.

---

## 5. Circuits

### 5.1 Power architecture and budget

**Rails**
| Net | Source | Voltage | Feeds |
|---|---|---|---|
| VBUS | USB-C | 4.75–5.5 V (USB spec); protected to 20 V abs max | BQ25887 VBUS, U_IN eFuse |
| BAT+ | Cell 2 (+) via F1 | 5.6–8.4 V (S-8252 UV 2.80 V/cell to 4.20 V/cell) | BQ25887 BAT/SNS, TPS56637 VIN, MAX17205 VBATT |
| **V5** | U_IN eFuse (USB) **or** TPS56637 (battery), diode-OR by voltage | **4.9–5.1 V on USB, 4.80 V on battery** (±1.5 %) | 3V3 buck, 5 port eFuses, V5_SENSE |
| +3V3 | TPS629210 from V5 | 3.3 V, 1 A | ESP32, mux, expander, LCD, pull-ups, LEDs |
| V5_1…5 | port eFuse outputs | V5 − ≤ 0.06 V | J1–J5 |

**How V5 is shared (the power path):**
- **USB only:** the buck is off (BAT+ absent; its EN UVLO ≈ 5.4 V keeps it off). V5 = VBUS through U_IN.
- **Battery only:** V5 = buck output, 4.80 V.
- **USB + battery:** USB holds V5 at ≈ 4.9–5.1 V, above the buck's 4.80 V set point, so the buck (Eco-mode, no forced PWM, so it never sinks current) is idle. **When the load exceeds the U_IN current limit**, U_IN regulates its current, V5 falls to 4.80 V and **the buck delivers the rest from the battery**. Full load therefore works on any USB source when a battery is fitted.
- **U_IN behaviour in that state (TPS25947 datasheet SLVSFC9C, rev. May 2026):** for I_LIM < I_OUT < 2 × I_LIM, transients shorter than ITIMER pass unlimited; once ITIMER expires (22 nF → ≈ 18 ms) the HFET **regulates the current at I_LIM and keeps doing so with no time-out** (§7.3.5.3, "the current limit starts regulating the HFET to actively limit the current"; Table 7-3: persistent overcurrent, current-limit variant → *Current Limit*, not latched, FLT low after t_ITIMER). The only exits are the load falling below I_LIM, or **thermal shutdown at T_J 154 °C**; the A variant then restarts after cooling by 10 °C plus t_RST (§7.3.8, Table 7-2). The current-limit foldback only applies below V_OUT 1.9 V (V_FB), far below 4.80 V. **So the load share is stable for as long as the buck holds V5 at 4.80 V**, provided U_IN stays below TSD (§5.6.1). If U_IN does hit TSD with a battery fitted, the buck takes the whole load (V5 stays regulated) and U_IN retries on its own: a graceful fallback, not an outage.
- U_IN's FLT is low during load sharing (Table 7-3), so it is a "USB at its limit" flag, not a fault (§8.9).
- **U_IN blocks reverse current** (true reverse blocking, 29 mV threshold), so the buck never back-feeds VBUS, the charger or the USB host (D5).
- With a weak USB source (VBUS < ≈ 4.88 V under load) the buck carries part of the load while the charger charges the pack from USB. This only costs efficiency; firmware sees it in the gauge current.
- The buck's high-side body diode can lift a battery-less BAT+ node to ≈ V5 − 0.6 V ≈ 4.3 V (µA leakage only). This is below the buck UVLO and below firmware's "battery present" threshold (§8.4).

**Loads** (V5 ≈ 4.9 V; port caps as E0003, owner Q3 v1.0)
| Load | Idle | Typical active | Operating peak | Cap / hard limit |
|---|---|---|---|---|
| ESP32-S3 (Wi-Fi) + logic + LCD on 3V3 | 0.10 A | 0.25 A | 0.60 A (TX burst + backlight) | 1 A (TPS629210) |
| **3V3 seen at V5** (η ≈ 90 %) | 0.08 A | 0.19 A | **0.45 A** | 0.75 A |
| E0001 (each), 5 V revision | 0.02 A | 0.2–0.35 A moving | **≤ 0.6 A** (own limit; a 10 V motor at 5 V stalls lower anyway) | eFuse 0.74–1.00 A |
| E0002, 5 V revision | 0.05 A | 0.2–0.5 A | ≈ 1.0 A operating, **≤ 2.0 A** peak | eFuse 1.80–2.20 A |
| **Ports total** | 0.13 A | 0.5 A | 2.2 A (4 faders moving + knob 1 A) | firmware budget 4.4 A; eFuse sum ≤ 6.2 A |

**V5 totals**
| Case | V5 current | V5 power | From the battery (η 92 %, at 6.4 V / 7.4 V) |
|---|---|---|---|
| Idle | 0.21 A | 1.0 W | 0.18 A / 0.15 A |
| Typical active | 0.7 A | 3.4 W | 0.58 A / 0.50 A |
| Operating peak | 2.65 A | 13 W | 2.2 A / 1.9 A |
| **Worst plausible** (4 × 0.6 A + 2.0 A + 3V3 peak) | **4.85 A** | **23.3 W** | **4.0 A / 3.4 A** |
| Hardware worst case (all eFuses at max, multi-fault) | 6.65 A | 32 W | 5.4 A / 4.7 A |

- **V5 converter sized for 6 A:** TPS56637 6 A rating, valley current limit 6.3–8.6 A (output limit ≈ 7–9 A). **Copper (v1.4): sized for a 4.6 A design current at ΔT ≤ 20 °C** (4.4 A firmware port budget + typical 3V3; 4.85 A worst-plausible peaks ≈ 22 °C, accepted); the pack path is sized for 5 A at ΔT ≤ 20 °C (4.0 A worst plausible at a 6.4 V pack), with F1 10 A and the buck limit as the backstops; inductor 3.3 µH, Isat ≥ 9 A (datasheet Table 4). Worst plausible (4.85 A) has 1.15 A margin. The hardware worst case is a multi-fault case: the buck current limit, then the port UVLO, are the backstops.
- **Buck dropout:** t_OFF(min) 300 ns max at 500 kHz → D_max ≈ 85 %, so V5 holds 4.80 V down to a pack of ≈ 5.9 V at 5 A (≈ 5.7 V light load). Firmware sheds the ports at 6.4 V (§8.6), so the ports never see the dropout region.
- **Battery current** ≤ 4.0 A worst plausible, ≤ ≈ 9 A by the buck current limit: inside F1 10 A, S-8252 OC ≈ 17–21 A, P50B 60 A. There is no charger BATFET in the discharge path any more, so **E0003's O-1 gap (6–20 A) is closed by the buck current limit**; a short on BAT+ itself is still covered by the S-8252 short detection and F1.
- **Runtime** (≈ 32 Wh usable): idle ≈ 29 h, typical active ≈ 8.5 h, continuous operating peak ≈ 2.3 h.

### 5.1.2 USB only, no battery: V5 back-feed into BAT+ (v1.2)
V5 → L1 → SW → TPS56637 high-side body diode → VIN = BAT+. At the tens of µA that flow, BAT+ sits **≈ 0.45 V below V5: ≈ 4.45 V typical, ≤ 5.05 V at USB 5.5 V**. This is why the buck's internal supply is up and its 200 Ω SW discharge runs. Effects (details and numbers in `docs/schematic_notes.md`):
- **BQ25887:** with CD high (reset default) nothing runs and no pin is stressed; the cell readings are undefined (MID floats) but add up to BAT+. If firmware wrongly enabled charging, the battery probe can see a "battery" (V5 feeds its 8–16 mA probe load), the charger charges the ≈ 20 µF on BAT+ to 8.4 V, terminates and cycles, and STAT blinks (the datasheet's no-battery behaviour). 8.4 V is inside every rating on BAT+ (charger 12 V, buck 28 V, gauge 20 V).
- **MAX17205** runs inside its **4.2–20 V VBATT operating range** (ADI MAX17201–MAX17215 datasheet, Electrical Characteristics, Power Supply, Notes 1–2; abs max VBATT −0.3 to +22 V; `docs/datasheets/MAX17201-MAX17215.pdf`): it runs and reads ≈ BAT+ (4.45–5.05 V). That is why §8.4 needs the 5.6 V threshold and the precharge probe. **S-8252** sees two over-discharged "cells" and keeps the discharge FET off, ≤ 8 µA. The reverse-cell LED strings can't conduct.
- **Latch / buck EN:** latch off → EN 54 mV, buck off. Button held → EN 0.98 V (1.11 V at USB 5.5 V), below the 1.18 V typical turn-on. A low-threshold part could enable, which is harmless: V5 is above the 4.79 V set point, so the buck doesn't switch.
- **Extra draw from V5 ≈ 24.6 mA**, 99.6 % of it the SW discharge (§13); the always-on V5 dividers add 62–69 µA in any state.
- **Battery detect:** at typical USB the window rejects with 0.55 V margin, but at USB 5.5 V the gauge can read ≈ 5.05 V. Hence the §8.4 rule.

### 5.1.1 V5 bulk and the USB-unplug transient (v1.1)
**Bulk on V5 (limited by the buck):** TPS56637 datasheet Table 4, 5 V row: **L 3.3 µH, effective C_OUT 20–100 µF** (typ 30 µF), feed-forward R8 20 kΩ + C9 100–220 pF. V5 therefore carries **2 × 47 µF / 16 V X5R 1210 at the buck output + 10 µF / 25 V 0805 at the five port eFuse inputs and the 3V3 buck input ≈ 85–95 µF effective at 5 V** (DC-bias derating ≈ 35 % on the 1210s, ≈ 40 % on the 0805s; the exact table is in `docs/schematic_notes.md`). **85 µF is used below.** The peripherals' capacitance sits behind the port eFuses (reverse blocking) and does not help V5.

**Event:** USB pulled while the battery is fitted and the buck is idle in Eco-mode (inductor current 0).
1. V5 falls from ≈ 4.95 V to the buck set point 4.79 V: at 4.85 A ≈ 3 µs. U_IN's reverse blocking opens within 1 µs (t_RCB).
2. The buck (D-CAP3) fires back-to-back on-pulses at minimum off-time (t_OFF(min) **300 ns max**; t_ON = V_OUT / (V_IN × 500 kHz)); with 3.3 µH the inductor current ramps at an average S = net rise per cycle / (t_ON + t_OFF). Extra dip ΔV ≈ I² / (2 × C × S).

| Pack | V5 load | S | Ramp | Dip | **V5 min** | Margin to port UVLO falling (3.80 V typ, **3.93 V max**) |
|---|---|---|---|---|---|---|
| 7.4 V | 4.85 A | 0.37 A/µs | 13 µs | 0.38 V | **4.42 V** | 0.49 V |
| 6.8 V | 4.85 A | 0.25 A/µs | 20 µs | 0.57 V | **4.23 V** | 0.30 V |
| **6.4 V** | **3.0 A** (§8.6 derating below 6.8 V) | 0.16 A/µs | 19 µs | 0.33 V | **4.47 V** | 0.54 V |
| 6.4 V | 4.85 A (not allowed by §8.6) | 0.16 A/µs | 30 µs | 0.86 V | 3.94 V | ≈ 0 — this is why §8.6 exists |

**The port UVLO does not trip on a USB unplug in any allowed state.** With the typical t_OFF(min) 200 ns the dips are ≈ 35 % smaller. The 3V3 rail is unaffected (TPS629210 at 100 % duty holds 3.3 V down to ≈ 3.5 V in). Plug-in is benign (V5 steps up to ≈ 5.0 V through U_IN's dVdt). Bench check at bring-up (§11.3).

### 5.2 USB-only operation and current budget (no battery)

The board reads the source's Rp level on CC1/CC2 (ESP32 ADC, §5.6) and sets U_IN's limit: **0.50 A** (reset state; Rp default), **1.37 A** (Rp 1.5 A) or **2.81 A** (Rp 3.0 A). Charging is off without a battery. V5 ≈ 4.9 V; 3V3 at its 0.45 A peak.

| Source (Rp) | U_IN limit | V5 power | **Port budget** | What works |
|---|---|---|---|---|
| USB 2.0/3.x port, Rp default (0.5/0.9 A) | 0.50 A (0.425–0.575 A) | ≤ 2.5 W | **ports off** (≈ 0.05 A) | MCU, Wi-Fi, LCD; programming. Average ≈ 0.2–0.3 A; Wi-Fi TX bursts (≈ 0.45 A at V5, < 18 ms) pass within the ITIMER blanking |
| 5 V / 1.5 A (Rp 1.5 A) | 1.37 A | 6.7 W | **≈ 0.9 A** | 1–2 faders moving, or the knob at low torque |
| **5 V / 3 A (Rp 3.0 A)** | 2.81 A | 13.8 W | **≈ 2.3 A** | **Typical use and the operating peak (2.2 A)**; not the 4.4 A worst case |
| **Any source + battery** | as above | + battery via the buck | **4.4 A** (full budget) | **Full load**; the battery supplies the difference (§5.1) |

**What happens when USB can't supply the load (no battery):**
1. Firmware budget first (§8.2): it knows the Rp level and limits fader moves / E0002 torque over I²C; it watches V5_SENSE.
2. If the load still exceeds U_IN's limit for > ITIMER (≈ 18 ms), **U_IN regulates its current at I_LIM** (it does not turn off, §5.1). With no buck to make up the difference, V5 sags, and at **3.80 V the port eFuses' UVLO cuts all ports**. V5 recovers; the 3V3 buck (works down to ≈ 3.5 V in, 100 % duty) keeps the MCU running. The ports come back only when firmware re-enables them (≥ 4.19 V rising and EN).
3. If the source trips before our limit (e.g. a 500 mA port overloaded): VBUS collapses, the board resets, and firmware restarts in the "Rp default" low-power mode.

With a battery fitted, step 2 never happens below the 4.4 A budget: the buck takes over at 4.80 V.

### 5.3 Charger — **TI BQ25887** (VQFN-24 4 × 4 mm) [new]

**Choice.** Candidates for "5 V USB → 2S":
| Part | For | Against | Verdict |
|---|---|---|---|
| **TI BQ25887** | 5 V-input boost charger for 2S, 2.2 A, I²C, ICO, VINDPM, **16-bit ADC (VBUS, IBUS, both cell voltages, TS, die temp)**, **integrated cell balancing (≤ 400 mA)**, cell OVP, JEITA with 103AT-2; VBUS abs max 20 V, OVP 6.2–6.6 V; DigiKey stock (BQ25887RGET 211, RGER 10 911) | No system output (system sits on BAT) — exactly what this topology needs | **Chosen** |
| TI BQ25883 / BQ25882 | Same family with NVDC power path | BQ25883: DigiKey stock 0; BQ25882 not listed; no balancing; NVDC would put the system behind a boost + buck (double conversion on USB) | Rejected |
| Injoinic IP2326 | Cheap, standalone | No I²C/ADC, no balancing, LCSC-only (BOM exception), thin documentation | Rejected |

**Settings**
- **ICHG 2.0 A** by firmware (max 2.2 A; P50B standard charge 5 A). From a 5 V / 3 A source with the system idle the input limit allows ≈ 1.6–1.8 A at 7.6 V; firmware sets IINDPM = source capability − measured system draw. Full charge from empty ≈ 3.5–4 h.
- **VREG 8.40 V** (4.20 V/cell). Cell OVP at 104 % (≈ 4.37 V) stops charging independently of the S-8252 (4.30 V).
- **ILIM pin: R_ILIM 374 Ω** → hardware cap 2.97 A (K_ILIM 1110). The register IINDPM (firmware) is lower.
- **PSEL: pulled high** (10 k to 3V3) → 500 mA default input limit until firmware writes IINDPM. ICO is then disabled; firmware enables it if wanted.
- **VINDPM 4.6 V** (firmware): if VBUS sags, the charger backs off before the system path does.
- **CD (active high = HIZ):** 10 k pull-up to 3V3 → **charging off at reset**; TCA9535 P05 drives it low to charge, only with a detected battery (§8.4). Same safe default as E0003's CE.
- **MID** → cell mid-point via **300 Ω** (datasheet, bottom-cell reverse protection). **CBSET** → mid-point via **39 Ω 1 %, 2512 (1 W)** → **≈ 108 mA** balancing, 0.45 W in the resistor (datasheet example 9.5 Ω = 400 mA is not needed for a matched P50B pair). Automatic balancing (default on) with **CB_CHG_DIS = 1** (default): charging pauses for each cell measurement, so the ≈ 20 mV offset across the protection FETs + R_SENSE at 2 A does not bias the bottom-cell reading.
- **TS ← NTC1** (Semitec 103AT-2, as E0003; the datasheet's recommended part) with the REGN divider for JEITA 0–60 °C.
- **Inductor 1 µH**, Isat ≥ 5 A (boost peak at 3.3 A input + ripple), datasheet reference IHLP-2525CZ-1R0 class. Caps: VBUS 1 µF + PMID 10 µF (≥ 10 V), SNS 44 µF (2 × 22 µF, ≥ 16 V), BAT 10 µF (≥ 16 V), REGN 4.7 µF, BTST 47 nF.
- **STAT** → amber LED; **INT** → GPIO5; **PG** → TCA9535 P16. I²C0 at **0x6A** (no clash with 0x20, 0x36, 0x0B).
- Battery quiescent: 12 µA (ADC off).

### 5.4 Battery pack, protection, balancing, fuel gauge [as E0003, BQ29209 removed]
**Unchanged from E0003 §5.4** (cells, Keystone 1121 holders and the mandatory P50B test fit, F1 10 A, S-8252AAG OV 4.30 / UV 2.80 / OC 0.150 V with 2 × PSMN2R0-30YLDX low-side, R_SENSE 5 mΩ between the FETs and GND, MAX17205 stack-only gauge with GND = PACK−, its series R and RC, NTC2 on the gauge, reverse-cell BAT54W clamps on the S-8252, reverse-cell LEDs, polarity marks).

Changes:
- **BQ29209, its series resistors and clamps, Q10/BAL_EN and the OV2 dual FET are removed** (owner Q2, v1.0): the BQ25887 balances (above) and provides a second, independent cell-OV stop. Ladder (per cell): VREG 4.20 V → **S-8252AAG OV 4.30 V** (charge FET off) → **BQ25887 cell OVP ≈ 4.37 V** (charger stops). Discharge: firmware 3.2 V/cell under load → port UVLO / buck dropout → S-8252 UV 2.80 V → P50B 2.5 V.
- **The MID → GPIO4 divider is removed**; per-cell voltages come from the BQ25887 ADC (works in battery-only mode).
- BAT+ (after F1) feeds the BQ25887 BAT/SNS, the TPS56637 VIN and the MAX17205 VBATT.
- When the S-8252 FETs are open, the gauge powers down (as E0003) and V5 falls to USB-only operation.

### 5.5 I²C host: ports, pull-ups, mux, protection [as E0003, 5 V thresholds]
Topology, mux, pull-ups, cable length (≤ 1.0 m, 26 AWG), series 220 Ω + TPD2E2U06 ESD: **as E0003 §5.5**. I2C0 devices: **BQ25887 0x6A, TCA9535 0x20, MAX17205 0x36 + 0x0B** (STUSB4500 gone).

**Per-port protection (J1–J5) — TPS259470ARPWR**
| Item | Value | Result |
|---|---|---|
| R_ILM | 3.83 kΩ (J1–J4), 1.65 kΩ (J5) | 0.87 A typ (0.74–1.00 A); 2.03 A typ (1.80–2.20 A) — as E0003 |
| **OVLO** | **1 MΩ / 249 kΩ 1 %** | **6.02 V rising / 5.47 V falling** (≈ 5.85–6.25 V with tolerances): above USB's 5.5 V max, below the 6.5 V the 5 V peripherals must withstand (§6) |
| **EN/UVLO** | **1 MΩ / 402 kΩ 1 %** (v1.1); 2N7002 pulls EN low (gate ← TCA9535 P00–P04, 100 k pull-up → **off at reset**) | **4.19 V rising / 3.80 V falling** (4.09–4.31 V / 3.72–3.93 V at the corners; rising max < 4.72 V battery V5 min) |
| ITIMER / dVdt | 22 nF (≈ 18 ms) / 1.8 nF (≈ 1 V/ms, ≈ 5 ms ramp) | as E0003 |
| FLT | → TCA9535 P10–P14, 10 k pull-up | |
| Port TVS | **SMF5.0A** after the eFuse | 5.0 V stand-off, 6.4 V min breakdown |
| Silkscreen | **"5V"** + port number + "E0001" / "E0002" | |

### 5.6 USB-C [as E0003, PD removed]
- **J11 GCT USB4105-GF-A**, west edge (as E0003).
- **CC1, CC2: 5.1 kΩ 1 % Rd to GND each** (dead-battery safe, no IC). Each CC also goes through **10 kΩ** to an ESP32 ADC1 pin (**CC1 → GPIO6, CC2 → GPIO7**) with 1 nF at the pin. The active CC reads ≈ 0.41 V (default USB), ≈ 0.92 V (1.5 A) or ≈ 1.68 V (3.0 A); the other ≈ 0 V. Firmware takes the higher one.
- **VBUS TVS: SMF9.0A** (common part, DigiKey). 9 V stand-off, 15.4 V clamp < BQ25887 20 V and TPS25947 abs max; a faulty 9–12 V source is blocked by U_IN OVLO (6.0 V) and the BQ25887 OVP (6.2–6.6 V).
- **U_IN (TPS259470ARPWR):** IN = VBUS, OUT = V5. OVLO 1 MΩ / 249 kΩ (6.02 V). EN/UVLO 1 MΩ / 390 kΩ → **4.28 V rising / 3.88 V falling**. **Current limit in three levels** (I_LIM = 3334 / R_ILM, SLVSFC9C eq. 7; tolerance from the datasheet test points):

| Level | R_ILM | I_LIM typ | Range | P06 USB_ILIM_1A5 | P07 USB_ILIM_3A0 | Use |
|---|---|---|---|---|---|---|
| **Reset / Rp default** | **6.65 kΩ** (base, to GND) | **0.50 A** | 0.425–0.575 A (datasheet test point) | 0 | 0 | USB 2.0/3.x host ports; default after reset and power-up |
| Rp 1.5 A | 6.65 k ∥ **3.83 kΩ** (leg A) = 2.43 kΩ | 1.37 A | ≈ 1.19–1.55 A | 1 | 0 | 5 V / 1.5 A sources |
| Rp 3.0 A | 6.65 k ∥ 3.83 k ∥ **2.32 kΩ** (leg B) = 1.19 kΩ | 2.81 A | ≈ 2.50–3.12 A | 1 | 1 | 5 V / 3 A sources |

  Each leg is a 1 % resistor in series with a **2N7002** (R_DS(on) ≤ 5 Ω ≪ 2.32 kΩ) to GND, gate ← TCA9535, **100 k gate pull-down → leg off at reset**. Legs are cumulative: firmware never sets P07 without P06 (P07 alone would give 1.94 A). 6.65 kΩ is the largest R_ILM the datasheet allows (549 Ω–6.65 kΩ).
- ITIMER 22 nF, dVdt 1.8 nF (limits plug-in inrush into the V5 bulk caps). FLT → TCA9535 P15.
- **D+/D−:** USBLC6-2SC6 (VBUS pin → +3V3) → 0 Ω → GPIO19/20, 90 Ω differential (as E0003). Shell 1 MΩ ∥ 4.7 nF to GND.

### 5.6.1 U_IN thermal check
In load sharing U_IN sits in current limit with V5 held by the buck, so it dissipates **P = (V_BUS − V5) × I_LIM** (the total drop across the HFET; the 28 mΩ R_DS(on) loss is part of it).

| Case | V_BUS | V5 | I_LIM | **P** |
|---|---|---|---|---|
| Typical (3 A charger, cable drop) | 5.10 V | 4.80 V | 2.81 A | 0.84 W |
| **Worst nominal** (PlaceRoute) | 5.25 V | 4.80 V | 2.81 A | **1.26 W** |
| Stacked corners (V_BUS max, V5 −1.5 %, I_LIM +11 %) | 5.25 V | 4.73 V | 3.12 A | **1.62 W** |

**θJA** (SLVSFC9C §6.4): **74.5 °C/W** on a JEDEC 2s2p board with no vias under the part, 41.7 °C/W on TI's board with 8 vias under it. The RPW package has no exposed pad, so vias under it would land in the IN/OUT pads, which the house rule forbids. **Design assumption: θJA ≤ 55 °C/W**, using the copper below (between the two datasheet cases: same 4-layer stack, larger pours, vias next to the pads instead of in them). Ambient inside the box: 40 °C. TSD 154 °C.

| Case | T_J at θJA 55 °C/W | T_J at JEDEC 74.5 °C/W |
|---|---|---|
| Worst nominal, 1.26 W | **109 °C** (45 °C margin) | 134 °C (20 °C margin) |
| Stacked corners, 1.62 W | **129 °C** (25 °C margin) | 161 °C → TSD: the buck takes the load and U_IN auto-retries (§5.1) |

**Decision:** keep **2.81 A** and the **4.80 V** set point, and reserve this copper at placement:
- U_IN on F.Cu, **≈ 15 × 12 mm keep area** including its passives. Keep the BQ25887, the 1 µH and 3.3 µH inductors and the TPS56637 ≥ 5 mm away (they heat the same copper).
- **IN (VBUS) pins → F.Cu pour ≥ 80 mm²** (e.g. 10 × 8 mm) right at the pads; **OUT (V5) pins → F.Cu pour ≥ 80 mm²**, which joins the V5 rail.
- **≥ 6 vias per pour** (0.3 mm drill / 0.6 mm pad), each ≥ 0.15 mm copper-to-copper from any pad, to the same net on In2 (V5 pour) and B.Cu (VBUS pour ≥ 100 mm²). **GND pin** to the In1 plane with ≥ 2 vias off the pad.
- No thermal-relief spokes on the U_IN pads (solid zone connection).

**Fallback, resistor change only:** if the prototype shows U_IN above 120 °C at 2.81 A, change leg B from 2.32 kΩ to **2.94 kΩ** (top level 2.50 A, stacked corners 1.46 W).

### 5.7 2S → 5 V buck — **TI TPS56637** (VQFN-HR-10 3 × 3) [new]
- VIN = BAT+ (5.6–8.4 V; 4.5–28 V part), **V_OUT 4.80 V** (FB 0.6 V: 100 kΩ / 14.3 kΩ class, exact values at capture), 500 kHz, D-CAP3, **MODE to GND → Eco-mode** (pulse-skipping, no reverse current: required for the diode-OR).
- **Inductor 3.3 µH, Isat ≥ 9 A, Irms ≥ 7 A** (datasheet Table 4; datasheet part Vishay IHLP3232DZER3R3M11, final part in the schematic BOM). Ripple at 8.4 V ≈ 1.25 A p-p, peak ≈ 6.6 A at 6 A. V5 bulk: **2 × 47 µF / 16 V X5R 1210** (CL32A476KOJNNNE) at the buck output plus 10 µF / 25 V at each eFuse input and the 3V3 buck input, **≤ 100 µF effective in total** (§5.1.1). Feed-forward 20 kΩ + C9 per Table 4.
- **OVP** at 125 % of 4.79 V ≈ 6.0 V: above USB's 5.5 V max on V5, so USB holding V5 high never trips it. **SW discharge** (200 Ω, datasheet §7.3.9) is on whenever EN is low: see §8.5. Input 2 × 10 µF/25 V + 100 nF.
- **EN** ← soft power latch (§5.9) through a divider from BAT+: **UVLO ≈ 5.4 V rising** (EN 1.18 V rising, 1.04 V falling), EN pin ≤ 2 V at 8.4 V (abs max 6 V).
- **PG** (open drain) → TCA9535 P17, 10 k to 3V3.
- Shutdown current 2 µA.

### 5.8 3V3 regulator — **TPS629210** [as E0003, input V5]
Same circuit as E0003 §5.11 with VIN = V5 (3–17 V part). Works at 100 % duty down to ≈ 3.5 V V5, so the MCU survives a port UVLO event.

### 5.9 Power button, latch, buttons, LEDs [E0003 + latch]
- **PWR button:** on-board tactile + **J12** JST-GH 2p for a panel button, PESD5V0L1UL at J12 (as E0003). Button closes **PB_RAW to GND**.
- **Soft power latch (new):** P-FET **Q_PL** (VDS ≥ 20 V, VGS ±12 V, SOT-23) from BAT+ to the buck EN divider, gate pulled to BAT+ by 1 MΩ. The gate is pulled low (via 10 kΩ) either by the button (PB_RAW, through a BAT54W) or by an N-FET driven by **PWR_HOLD (GPIO36)**, 100 k gate pull-down.
  - **On:** press → Q_PL on → buck on → 3V3 → firmware sets PWR_HOLD high within the press.
  - **Off:** long press, detected on **GPIO21** (PB_RAW via BAT54W, 10 k pull-up to 3V3, as E0003) → firmware drops PWR_HOLD → buck off.
  - With USB plugged in, the MCU runs from USB whatever the latch state (owner Q4, v1.0); firmware decides whether the battery may supply (PWR_HOLD).
  - **Off drain ≈ 32 µA**: BQ25887 12 µA + MAX17205 12 µA + S-8252 6 µA + buck 2 µA (≈ 0.25 Ah/year).
- **BOOT** (GPIO0) and **RESET** (EN, 10 k / 1 µF): as E0003.
- LEDs: green status (GPIO40), amber charge (BQ25887 STAT), 2 × red reverse-cell (as E0003).
- **No test points.**

### 5.10 System-bus I/O expander — TCA9535 (0x20) [as E0003, re-mapped]
| Pin | Net | Dir | Reset state |
|---|---|---|---|
| P00–P04 | PORT1_OFF … PORT5_OFF | out | 100 k pull-up → **port off** |
| P05 | CHG_CD (BQ25887 CD, active high) | out | 10 k pull-up → **charging off** |
| P06 | USB_ILIM_1A5 (U_IN leg A, 2N7002 gate) | out | 100 k pull-down → leg off |
| P07 | USB_ILIM_3A0 (U_IN leg B, 2N7002 gate) | out | 100 k pull-down → leg off → **U_IN 0.50 A at reset** |
| P10–P14 | PORT1_FLT_N … PORT5_FLT_N | in | 10 k pull-up |
| P15 | USBIN_FLT_N (U_IN FLT: low = at its current limit, or TSD) | in | 10 k pull-up |
| P16 | CHG_PG_N (BQ25887 PG) | in | 10 k pull-up |
| P17 | BUCK_PG (TPS56637 PG) | in | 10 k pull-up |

### 5.11 LCD and switches [as E0003]
- **J10 EYESPI** (Hirose FH12-18S-0.5SH), Vin = +3V3, wiring as E0003 §5.7 (SCK 12, MOSI 11, MISO 13, TCS 10, DC 14, RST 39, LITE 47, SDCS 41, INT 42, SCL/SDA mux ch5, 33 Ω series on SCK/MOSI). DNP 0 Ω option: **GPIO37 → GP1** (GP2 option dropped: GPIO36 is now PWR_HOLD).
- **J6–J9 switches:** as E0003 §5.8 (4.7 k pull-up, PESD5V0L1UL, 1 k, 100 nF; GPIO15–18).

---

## 6. 5 V port spec — host interface for the future 5 V revisions of E0001 and E0002

**Status: draft with this spec.** "Host" = E0005; "peripheral" = the 5 V revisions of E0001 / E0002 (not designed yet, out of scope). **E0001 rev C and E0002 rev B (PBUS 6–9 V) will not work on E0005.**

### 6.1 Connectors and pinouts (unchanged)
| E0001: JST-GH 4p SM04B-GHS-TB | E0002: JST-GH 6p SM06B-GHS-TB |
|---|---|
| 1 **+5V**, 2 SCL, 3 SDA, 4 GND | 1–2 **+5V**, 3 SCL, 4 SDA, 5–6 GND |

MP = GND. Cables 1:1, 26 AWG, ≤ 1.0 m.

### 6.2 Voltage and current
| Parameter | Host guarantees at its connector | Peripheral must |
|---|---|---|
| +5V normal range | **4.70–5.25 V** (USB 4.9–5.1 V, battery 4.80 V ± 1.5 %) | **operate fully at 4.2–5.5 V at its connector** (after ≤ 1 m cable: E0002 at 2 A loses ≈ 0.39 V, E0001 at 0.6 A ≈ 0.21 V) |
| Over-voltage | eFuse **OVLO 5.85–6.25 V** | **withstand ≥ 6.5 V continuous** |
| Under-voltage | eFuse UVLO 3.80 V falling / 4.19 V rising | brown out cleanly below 3.7 V |
| Turn-on | off at host reset; one port at a time; ≈ 1 V/ms ramp | input capacitance ≤ 220 µF; motor disabled until the host enables it over I²C |
| Current, E0001 (GH4) | eFuse 0.74–1.00 A | **≤ 0.6 A** continuous and peak (owner Q3) |
| Current, E0002 (GH6) | eFuse 2.03 A typ (1.80–2.20 A), ≈ 18 ms blanking | **≤ 2.0 A** continuous and peak (owner Q3) |
| Total for all ports | firmware budget 4.4 A with battery; per §5.2 on USB only | — |
| Back-feed | host eFuse blocks reverse current | must not source current into +5V |

### 6.3 I²C, behaviour rules, addresses
As E0003 §6.5–6.6: 3.3 V logic, host 4.7 kΩ pull-ups, no peripheral pull-ups, 5 V-tolerant pins, no back-powering, 400 kHz, E0001 0x30–0x37, E0002 0x28–0x2F; the host may switch a port off at any time; the peripheral's own current limit is primary.

### 6.4 Marking
Host: **"5V"** + port number + "E0001"/"E0002" next to every port. Peripherals: "5V" at the connector.

---

## 7. Pin assignment — ESP32-S3-WROOM-1-N16R2
Changes from E0003 §7 in **bold**. Strapping pins 0/3/45/46 stay free except BOOT. ADC pins are all on ADC1 (works with Wi-Fi).

| GPIO | Net | Function |
|---|---|---|
| 0 | BOOT | strapping, BOOT button, 10 k pull-up |
| 1 / 2 | I2C1_SDA / I2C1_SCL | → PCA9548A |
| 3 | — | strapping, NC |
| **4** | **V5_SENSE** | **ADC1_CH3: V5 via 100 k / 100 k + 100 nF (≤ 2.75 V at 5.5 V)** |
| 5 | CHG_INT_N | **BQ25887** INT, 10 k pull-up |
| **6** | **CC1_SENSE** | **ADC1_CH5, 10 k from CC1** |
| **7** | **CC2_SENSE** | **ADC1_CH6, 10 k from CC2** |
| 8 / 9 | I2C0_SDA / I2C0_SCL | system bus |
| 10–13 | LCD_CS / MOSI / SCK / MISO | FSPI IO_MUX |
| 14 | LCD_DC | |
| 15–18 | SW1–SW4 | RTC inputs |
| 19 / 20 | USB_D− / USB_D+ | native USB |
| 21 | PWR_BTN_N | RTC, wake source |
| 35 | GAUGE_ALRT_N | MAX17205 ALRT via 1 kΩ, 10 k pull-up |
| **36** | **PWR_HOLD** | **soft power latch hold (out), 100 k pull-down** |
| 37 | SPARE37 | DNP 0 Ω to EYESPI GP1 only |
| 38 | MUX_RST_N | PCA9548A RESET, 10 k pull-up |
| 39 | LCD_RST | |
| 40 | LED_STATUS | green LED |
| 41 | LCD_SDCS | |
| 42 | TOUCH_INT_N | |
| 43 / 44 | U0TXD / U0RXD | NC (console via USB CDC) |
| 45, 46 | — | strapping, NC |
| 47 | LCD_LITE | LEDC PWM |
| **48** | **EXP_INT_N** | **TCA9535 INT, 10 k pull-up** (moved from GPIO7) |
| EN | EN | RESET button, 10 k / 1 µF |

---

## 8. Firmware constraints the hardware relies on
1. **Power-up:** MCU first; ports, charging and the high USB limit off. Read CC (Rp level), V5_SENSE, the gauge, BQ25887 ADC; then set PWR_HOLD (on battery) and enable ports one at a time ≥ 10 ms apart.
2. **Budget:** port budget = 4.4 A with a battery; without one, per §5.2 (Rp level): ports off on Rp default, ≈ 0.9 A on 1.5 A, ≈ 2.3 A on 3.0 A. Enforce by limiting moves/torque over I²C, then by shedding ports. Feedback: V5_SENSE (< 4.75 V on USB-only = overload), gauge current, BQ25887 IBUS.
3. **VBUS budget (hard rule).** The total VBUS current is **U_IN + the BQ25887 input**, and both come out of the one source budget I_SRC (from Rp: default → 0.5 A, 1.5 A, 3.0 A):
   **I_LIM(U_IN setting, nominal) + IINDPM(BQ25887) ≤ I_SRC**, and the charger is enabled (CD low) only when the IINDPM this leaves is ≥ 0.5 A (its minimum).

   | Source (Rp) | Allowed settings (U_IN level + charger IINDPM) |
   |---|---|
   | Default (USB 2.0/3.x host) | U_IN 0.50 A, **charger off** (no charging from a plain host port; the battery runs the extra load if fitted) |
   | 1.5 A | U_IN 1.37 A + charger off, **or** U_IN 0.50 A + IINDPM 1.0 A (charge mode, light system load) |
   | 3.0 A | U_IN 2.81 A + charger off, **or** U_IN 1.37 A + IINDPM 1.6 A, **or** U_IN 0.50 A + IINDPM 2.5 A |

   - Change order: **lower first, raise second** (when moving to a higher U_IN level, first reduce IINDPM or set CD high, then set the leg; the other way round when moving down).
   - After reset the hardware is already inside every budget (U_IN 0.50 A, charger HIZ via CD pull-up, BQ25887 PSEL high → 500 mA default IINDPM, which only applies once firmware enables it).
   - Re-read CC after every attach; on detach go back to the reset settings.
   - With a battery fitted, a U_IN level below the system load is fine: the buck makes up the difference (§5.1).
4. **Charging:** CD low only with a detected battery (v1.2): **auto-enable only for a pack ≥ 5.6 V** (the S-8252 UV level) **and ≤ 8.6 V**, with both BQ25887 cell readings 2.8–4.3 V. A pack reading 5.0–5.6 V is charged only after a **precharge probe**: CD low with IPRECHG 150 mA for 50 ms; with no battery BAT+ jumps above 6.5 V within ≈ 1 ms (abort, CD high), while a real pack rises only millivolts. Below 5.0 V: no battery. Without a detected battery keep CD high and PWR_HOLD low (but see §8.5 with a battery). ICHG 2.0 A, VREG 8.40 V, IINDPM = source limit − system draw, VINDPM 4.6 V. Service or disable the BQ25887 watchdog (160 s). Keep CB_CHG_DIS = 1.
5. **Off and PWR_HOLD:** long press → ports off → PWR_HOLD low. **While USB is attached and a battery is fitted, keep PWR_HOLD high** (also in "off", owner Q4): with EN low the TPS56637 SW discharge (200 Ω) would draw ≈ 25 mA from USB; with EN high and V5 held by USB the buck idles in Eco-mode and the battery is not used (ports off). On USB detach in "off", drop PWR_HOLD. In USB-only/no-battery the ≈ 25 mA stays (buck VIN back-fed, §13).
6. **Low battery:** **below a 6.8 V pack (under load), limit the V5 load to ≤ 3.0 A** (port budget ≤ 2.5 A; keeps the USB-unplug dip clear of the port UVLO, §5.1.1); ports off at 3.2 V/cell (6.4 V pack); PWR_HOLD low at 3.0 V/cell.
7. **Temperature:** ports off above 60 °C; charging JEITA 0–60 °C.
8. **Gauge:** as E0003 §8.8 (stack-only, shadow RAM in development, one NV write in production).
9. **Mux** and **port eFuse faults:** as E0003 §8.9–8.10. **USBIN_FLT_N low is normal during load sharing** (U_IN at its limit, §5.1): with a battery, it means the battery is supplying the difference, so reduce charger IINDPM and keep the port budget; without a battery it means overload, so shed ports. If it stays low while V5_SENSE shows V5 > 4.9 V (USB not limiting), treat it as a U_IN thermal shutdown and drop to the next lower U_IN level for ≥ 10 s.
10. **Backlight / switches:** as E0003.
11. **Battery-level fallback:** the primary battery level is the MAX17205 (SoC, remaining time). If the gauge is not fitted (DNP) or not responding, firmware uses the **BQ25887 ADC** (VBAT and the two cell voltages; it works in battery-only mode, REGN on during conversions) with an OCV-vs-SoC table for the P50B, read at low load. The hardware supports both without changes.

---

## 9. Mechanical (PCB only)
- **Stack-up:** 4-layer 1.6 mm, JLC **JLC04161H-3313** (as E0003; 90 Ω USB pair). L1 parts/signals/power pours, L2 solid GND, L3 V5 + BAT+ pours and slow signals, L4 GND, holder lugs, protection parts.
- **Outline 125 × 73 mm** (v1.3: E0003's 125 × 65 mm extended 8 mm north for the port band; board-level Edge.Cuts, R3 corners), **4 × M3** 4 mm from the corners (`E0005_board:Holes_4xM3_125x73`), **E0003 edge plan** (Keystone 1121 footprint/STEP at E0003's positions): USB-C + power stage (U_IN, BQ25887 + 1 µH, TPS56637 + 3.3 µH, 3V3) on the **west** side off the cells; ports J1–J5 on the **north** edge with eFuse/TVS/ESD and "5V" labels; ESP32-S3 with the antenna keep-out at the **east** edge (≥ 15 mm to the cans); switches, J12, power button and EYESPI on the **south** edge; holders on the bottom.
- High-current paths: BAT+ → F1 → buck VIN, buck → V5 → port eFuses, and VBUS → U_IN → V5 carry up to ≈ 6 A: pours on two layers or ≥ 3 mm with via stitching. R_SENSE Kelvin to the gauge.
- Bottom standoffs ≥ 25 mm; top parts ≤ 12 mm (as E0003).
- House rules in R8: no test points, no vias in pads, 45° tracks, `.kicad_dru` with JLC + no-via-on-pad rules.

---

## 10. BOM plan (DigiKey-preferred; common parts from E0003 `bom/common_parts_across_projects.*`)
**Reused from E0003 (same MPN):** ESP32-S3-WROOM-1-N16R2 · TPS629210 + DFE252012PD-2R2M=P2 · S-8252AAG-M6T1U · 2 × PSMN2R0-30YLDX · MAX17205G+ · 5 mΩ sense · F1 Littelfuse 0452010.MRL · PCA9548APW · TCA9535PWR · **TPS259470ARPWR × 6** (5 ports + U_IN) · 2N7002-7-F (5 port EN + 2 U_IN legs + latch hold) · BAT54W,135 · USBLC6-2SC6 · TPD2E2U06DRLR × 5 · PESD5V0L1UL,315 × 5 · **SMF9.0A × 1** (VBUS) · Semitec 103AT-2 × 2 · Keystone 1121 × 2 · SM04B-GHS-TB × 4 · SM06B-GHS-TB(LF)(SN) · SM02B-GHS-TB × 5 · FH12-18S-0.5SH(55) · USB4105-GF-A · LEDs LTST-C191K* · 47 µF 1210 CL32A476KOJNNNE (V5 bulk × 2, charger SNS × 2) · all common passives (100 nF GRM155R71H104KE14D, 10 µF TMK212BBJ106MG-T, 22 µF CL21A226KQCLRNC, 1 nF GRM155R71H102KA01D, 47 nF GRM155R71H473KE14D, 4.7 k RK73H1ETTP4701F, Yageo RC0402 resistors).

**New:**
| Ref (planned) | Part | Qty | DigiKey (2026-10-27) | Note |
|---|---|---|---|---|
| U2 | **TI BQ25887RGER** (cut tape) | 1 | 296-53517-1-ND, 10 911 in stock (RGET is T&R only, 211 pcs, MOQ 250) | charger (PlaceRoute, after the schematic review) |
| U4 | **TI TPS56637RPAR** | 1 | 296-TPS56637RPARTR-ND, 14 313 | 2S → 5 V buck; check a cut-tape listing at BOM time |
| L2 | 1 µH, Isat ≥ 5 A, ≤ 20 mΩ (Vishay IHLP-2525CZ-1R0 class) | 1 | at BOM time | charger inductor |
| R_CB | 39 Ω 1 % 2512 1 W | 1 | at BOM time | balancing |
| D (ports) | **SMF5.0A** (Littelfuse) | 5 | at BOM time | replaces SMF9.0A at the ports |
| Q_PL | P-FET 20 V, VGS ±12 V, SOT-23 | 1 | at BOM time | soft power latch |

**Removed from E0003:** STUSB4500, BQ25798 + its inductor, BQ29209 (owner Q2), TVS2200DRVR (BOM exception gone), mid-point divider, Q10, OV2 FET.

---

## 11. Schematic-capture checks
1. BQ25887 reference schematic (datasheet §9.2): caps, BTST, REGN, TS divider for 103AT-2 JEITA, ILIM; MID 300 Ω and CBSET with the low-side protector (B− vs GND offset; CB_CHG_DIS).
2. BQ25887 behaviour with CD high and no battery; with the buck back-feed (BAT+ ≈ 4.3 V) and the gauge.
3. TPS56637 Eco-mode light-load behaviour with V5 held above its set point by USB (no sinking, no output overshoot when USB is pulled); USB-unplug dip at full load per §5.1.1 (bench, first bring-up); FB divider for 4.80 V; EN divider with the 4 µA hysteresis current; loop stability with the Table 4 L/C and feed-forward (load-step test).
4. U_IN TPS259470A: R_ILM legs with the 2N7002s; thermal case in §5.6.1 (copper and vias as reserved there); start-up into the V5 bulk caps (dVdt).
5. Port eFuse OVLO/UVLO dividers at the corners (5.5 V never trips OVLO; battery 4.72 V min stays above UVLO rising 4.31 V max).
6. CC sense: 10 kΩ + ADC leakage does not shift the Rd (5.1 kΩ) reading beyond the Type-C windows.
7. Soft power latch: Q_PL VGS at 8.4 V, button + PWR_HOLD logic, GPIO21 clamping, behaviour with USB present.
8. As E0003 §11: P50B test fit in the 1121, EYESPI pin order, ESP32-S3 pin check, NTC mounting, MAX17205 tie-offs.

---

## 12. Decided by the owner / brief
| Item | Decision |
|---|---|
| Layers / MCU | 4-layer, ESP32-S3-WROOM-1-N16R2 |
| Battery | 2 × Molicel P50B 2S, battery level measured on the ESP32 |
| USB | USB-C, native USB programming + charging; runs from USB without a battery |
| 5 V only | **Option A:** plain 5 V USB, no PD; one protected 5 V rail for 3V3 and all ports; USB power path + 2S → 5 V buck; 5 V boost charger |
| Connectors | EYESPI (Adafruit 4311), 4 × switch, 4 × E0001, 1 × E0002, pinouts unchanged, +5 V, "5V" silkscreen |
| Size | no strict limit |
| Peripherals | E0001/E0002 5 V revisions out of scope |
| House rules | §2.1 R8 |
| Battery level (Q1) | **MAX17205 fuel gauge kept**; BQ25887 ADC as firmware fallback |
| BQ29209 (Q2) | **Dropped**; the BQ25887 balances, S-8252 is the hardware cell OV/UV |
| Port limits (Q3) | **E0001 ≤ 0.6 A, E0002 ≤ 2.0 A, firmware budget 4.4 A** (E0003 values) |
| Off with USB (Q4) | **Board stays on from USB and charges** |
| Repository (Q5) | Private GitHub `Karpuls/E0005-esp32-s3-5v-controller`, push at every milestone |
| Placement / routing | Placement with the KiStack `layout-placement` scripts; routing by hand or script via IPC only (`kicad-layout`); **no autorouters of any kind** |

---

## 13. Risks
| Risk | Mitigation |
|---|---|
| Flat-top P50B vs the polarized 1121 | Sample test fit before the PCB order (as E0003) |
| E0001 rev C / E0002 rev B (6–9 V) plugged into a 5 V port | They brown out (below their 5.5 V minimum); no damage expected. Silkscreen "5V" |
| USB-only load above the source | Rp-based firmware budget; U_IN limit; port UVLO keeps the MCU alive (§5.2) |
| Weak USB source (< 4.88 V) lets the buck carry the load while charging | Efficiency loss only; firmware sees it on the gauge |
| U_IN heating in current limit with the buck holding V5 | ≤ 1.40 W worst case → T_J ≤ 124 °C with the §5.6.1 copper (≤ 144 °C even at JEDEC θJA); at TSD the buck takes the load and U_IN auto-retries |
| No charging from a plain USB host port (Rp default) | VBUS budget rule §8.3; charge from a 1.5 A / 3 A USB-C source |
| V5 dip on USB unplug at full load and low battery | UVLO 3.80 V, ≤ 3.0 A below 6.8 V pack (§8.6), bench check (§5.1.1) |
| TPS56637 SW discharge ≈ 25 mA (0.12 W) whenever EN is low and V5 is up | PWR_HOLD rule §8.5; remains in USB-only/no-battery (≈ 5 % of the 0.5 A default budget); chip temperature checked at bring-up |
| V5 at 4.80 V on battery + 1 m cable at 2 A → 4.4 V at E0002 | §6.2 requires peripherals to work from 4.2 V |
| Buck dropout below ≈ 5.9 V pack at full load | Firmware ports-off at 6.4 V |
| BQ25887 balancing current (≈ 108 mA) vs a strongly mismatched pair | Matched-pair cells; S-8252 per-cell OV is the hard stop |
| Hand assembly of QFNs (BQ25887, TPS56637, 6 × TPS259470 2 × 2, MAX17205) | Stencil + hot plate, as E0003 |

---

## 14. Owner questions — answered 2026-10-27 (all as recommended)
| # | Question | Answer |
|---|---|---|
| **Q1** | **Battery level:** keep E0003's **MAX17205 fuel gauge** (SoC %, remaining time, pack current; read by the ESP32 over I²C), or measure only the pack voltage with a resistor divider on an ESP32 ADC pin (simpler, voltage-based estimate, ±5–10 % SoC)? | Owner: **Keep the MAX17205** |
| **Q2** | **Drop the BQ29209** balancer/secondary-OV chip? The new charger balances the cells itself (≈ 110 mA) and stops charging on cell over-voltage; the S-8252 stays as the hardware cell OV/UV protector. | Owner: **Drop it** |
| **Q3** | **Port current for the future 5 V peripherals:** keep E0003's numbers (E0001 ≤ 0.6 A, eFuse 0.74–1.00 A; E0002 ≤ 2.0 A, eFuse 2.0 A nominal) and the firmware budget of 4.4 A? Without a battery the ports get ≈ 2.3 A on a 5 V / 3 A charger and ≈ 0.9 A on 1.5 A. | Owner: **Yes** |
| **Q4** | **"Off" with USB plugged in:** the board then keeps running from USB (it charges and can show the charge state; the battery is not used). OK, or should "off" also cut USB power to the MCU and ports? | Owner: **OK as proposed** |
| **Q5** | **GitHub:** create `Karpuls/E0005-esp32-s3-5v-controller` (private, like E0003) and push at milestones? Local git commits happen anyway. | Owner: **Yes, private repo, push at every milestone** |
