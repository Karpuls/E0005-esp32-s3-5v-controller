# E0005 rev A pre-order list

Things to do or confirm before (or when) ordering the PCB and parts, and the bench checks to run at bring-up. Quantities are per board. The parts data is in `E0005_revA_BOM.csv` and `bom/notes.md`.

## 1. Confirm at order time (DigiKey)
| Item | Ref | Qty | DigiKey PN | Action |
|---|---|---|---|---|
| **BQ25887RGER** (2S boost charger) | U2 | 1 | **296-53517-1-ND** (cut tape), 10 911 in stock on 2026-10-27 | Confirm the cut-tape listing and stock when ordering. The RGET T&R listing is 211 pcs with MOQ 250, so don't use it |
| **TPS56637RPAR** (6 A buck) | U17 | 1 | Lookup returned only the T&R listing 296-TPS56637RPARTR-ND (14 313, MOQ 3000) | **Find the cut-tape (CT) / Digi-Reel PN** when ordering |

## 2. Mechanical test fit (before ordering the PCB)
- **Molicel P50B in the Keystone 1121** (BH1, BH2): test-fit a flat-top P50B on a sample holder. Check that it seats against the contacts with the flat top, and whether the holder's **polarizing ribs** stop a flat-top cell. If it fails, a different holder needs a new footprint. Carried over from E0003 (O-5).

## 3. Impedance (USB 90 Ω): **confirmed**
- **Confirmed: W 0.153 / S 0.20 mm, coplanar with a 0.30 mm gap to the pour.** Source: JLC impedance calculator, JLC04161H-3313, L1 over L2, 2026-10-28 (owner).
- The board's USB_DP/USB_DN are routed at this width. At order time:
  - select **impedance control** with stackup **JLC04161H-3313**;
  - give the requirement as "90 Ω differential, USB_DP/USB_DN, L1 ref L2".

## 4. Board review items (gerber review): **closed**
- F-1 (V5 via in L1 pad 2) and F-2 (FET_D vias in the Q1/Q2 tab gap) were found in the preliminary run and **fixed in routing** (FIX_COMMIT).
- Details in [docs/gerber_review.md](docs/gerber_review.md).

## 5. Non-DigiKey parts (order first)
| Item | Ref | Qty | Source | Note |
|---|---|---|---|---|
| SM04B-GHS-TB (JST GH 4-pin) | J1–J4 | 4 | **LCSC C189895** (SM04B-GHS-TB(LF)(SN)), 2305 in stock (E0003 data 2026-10-18) | DigiKey 455-1566-1-ND had 0 stock; LCSC minimum order 5 |
| SM02B-GHS-TB (JST GH 2-pin) | J6–J9, J12 | 5 | **LCSC C189893** (SM02B-GHS-TB(LF)(SN)), 29 910 in stock | DigiKey 455-1564-1-ND had 0 stock |
| EYESPI cable, 18-pin 100 mm | off-board | 1 | **Adafruit 5239** (adafruit.com/product/5239), in stock (2026-10-10) | DigiKey 1528-5239-ND at 0 |
| Molicel INR21700-P50B 5000 mAh, flat top | off-board | 2 | **nkon.nl / akkuteile.de** (eu.nkon.nl/molicel-inr21700-p50b-5000mah-50a.html), stock not verified | Matched pair. Not sold by DigiKey. Test fit first (item 2) |
| Adafruit 2.0" 320×240 IPS (PID 4311) | off-board | 1 | DigiKey 1528-4311-ND (555) | DigiKey part, listed here as an off-board item |

## 6. Bench checks at bring-up (no test points; use USB and component pads)
| ID | Check | Pass criterion / action |
|---|---|---|
| **O-1** | **TPS56637 load-step stability** on battery: V5 load step 0.5 → 4 A, watched at C75/C76 | No ringing or overshoot beyond the D1 window (4.70–5.25 V at the port). If it rings, change the feed-forward cap **C79 from 100 pF to 220 pF** |
| **O-2b** | **TPS56637 temperature with the SW discharge active**: USB only, no battery, buck EN low (≈ 25 mA through the 200 Ω SW discharge, VIN back-fed from V5) | U17 temperature rise acceptable (thermal camera, 30 min) |
| **O-4** | **USB-unplug V5 dip at full load** (4.4 A port budget, battery fitted): unplug USB and scope V5 at a port | The port eFuse UVLO (3.80 V falling) must not trip; V5 must stay in the D1 window (SPEC §5.1.1) |
| **O-4** | **U_IN (U16) temperature in current limit** at the 2.81 A setting (SPEC §5.6.1) | Acceptable rise. If it runs hot, use fallback leg B (R_ILM 2.94 k) |
| — | Normal bring-up | Flash over native USB; check 3V3; I²C scan (BQ25887, MAX17205, TCA9535, PCA9548A); charger ADC per-cell readings; port eFuse limits |

## Closed
- **Impedance:** confirmed at JLC (item 3).
- **E0003 BOM exception TVS2200DRVR (LCSC):** gone. VBUS uses SMF9.0A (DigiKey).
