# E0005 sourcing notes (Phase 2 schematic, 2026-10-27, SPEC v1.0)

**BOM:** `bom/E0005_digikey_bom.csv`, E0003 column format (Supplier, Qty, QtyBasis, References, Value, Footprint, MPN, Manufacturer, SupplierPN, Stock, Lifecycle, UnitEUR, LeadWeeks, DNP, OwnerStock, Notes). **Generated** from the schematic fields by `build/scripts/make_bom.py`: never edit the CSV by hand; change `build/scripts/gen_sch.py` (MPN tables) and regenerate.
- 89 lines: 85 on-board lines (272 parts, R60 DNP) + E0003's off-board lines (display, EYESPI cable, 2 cells).
- Every symbol carries `MPN`, `Manufacturer`, `Supplier`, `Supplier PN` (the E0003 field set).

**Data sources (no BOM-wide API sweep):**
- Parts reused from E0003: stock/price/lead time copied from E0003's API-checked BOM (`E0003/bom/E0003_digikey_bom.csv` + `fab/E0003_revA/E0003_revA_BOM.csv`, 2026-10-18), not re-queried.
- New parts: one pcbparts `digikey_get_part` call each on 2026-10-27, stored in `bom/new_parts_digikey.csv` (price in USD, 1-piece). The lookup returns the tape & reel listing; the BOM uses the matching cut-tape PN (…CT-ND / …-1-ND) where the pattern is standard.

## New parts (all DigiKey, Active)
| Ref | MPN | DigiKey | Stock 2026-10-27 | Note |
|---|---|---|---|---|
| U2 | BQ25887RGET | 296-53518-2-ND | 211 (T&R, MOQ 250) | **stock exception, see below** |
| U17 | TPS56637RPAR | 296-TPS56637RPARTR-ND | 14 313 (T&R) | cut-tape PN to confirm at order |
| L2 | IHLP2525CZER1R0M01 (Vishay) | 541-1006-1-ND | 38 987 | 1 µH, 11 A / 22 A sat, 10 mΩ; KiCad `L_Vishay_IHLP-2525` |
| R147 | RMCF2512FT39R0 (Stackpole) | RMCF2512FT39R0CT-ND | 34 038 | 39 Ω 1 % 1 W 2512 (same series as E0002's RMCF2512 330R) |
| D19 D21 D23 D25 D27 | SMF5.0A (Littelfuse) | F5748CT-ND | 21 423 | E0001/E0002 common part |
| D12 | TPD1E10B09DPYR (TI) | 296-30405-1-ND | 48 491 | 9 V ESD for PB_RAW (replaces PESD5V0L1UL there, schematic notes D-4) |
| Q13 | AO3401A (AOS) | 785-1001-1-ND | 321 804 | E0001/E0002 common part |
| C79 | GRM1555C1H101JA01D | 490-5922-1-ND | 107 905 | 100 pF C0G (buck feed-forward) |
| resistors | Yageo RC0402FR-07: 374R, 300R, 5.1k, 6.65k, 2.32k, 53.6k, 69.8k, 200k, 249k, 365k, 390k | 311-/YAG…CT-ND | 7 547 – 1.26 M | all ≥ 10× board quantity |
| R148, R155 | RC0402FR-0739KL (39k), RC0402FR-0720KL (20k) | 311-39.0KLRCT-ND, 311-20.0KLRCT-ND | not re-queried | E0002 common parts |

## Stock exceptions / substitutions
1. **BQ25887RGET (U2):** the DigiKey lookup shows only the T&R listing 296-53518-2-ND, 211 pcs, MOQ 250 (no cut-tape result). SPEC §3/§10 noted **BQ25887RGER** with 10 911 on reel. Action at order time: buy RGER as cut tape / Digi-Reel (same RGE package and footprint) or confirm an RGET cut-tape listing. The schematic MPN stays BQ25887RGET (SPEC part).
2. **14.3k (RC0402FR-0714K3L): 0 stock** → TPS56637 FB changed to **69.8k / 10.0k** (4.788 V), schematic notes D-2.
3. **SNS caps:** no common 22 µF ≥ 16 V part → 2 × 47 µF/16 V 1210 CL32A476KOJNNNE (the V5 bulk part), schematic notes D-1.
4. **Carried over from E0003 (unchanged):** SM04B-GHS-TB (J1–J4) and SM02B-GHS-TB (J6–J9, J12) on **LCSC** (DigiKey 0 stock on 2026-10-18); EYESPI cable Adafruit 5239 direct; Molicel P50B from nkon.nl / akkuteile.de.
5. **E0003 BOM exception removed:** TVS2200DRVR (LCSC) is gone; VBUS uses SMF9.0A (DigiKey).

## Common-parts use
All passives use E0003's common MPNs where the value exists (100 nF GRM155R71H104KE14D, 10 µF TMK212BBJ106MG-T, 22 µF CL21A226KQCLRNC, 47 µF CL32A476KOJNNNE, 1 nF, 1.8 nF, 22 nF, 47 nF, 4.7 µF, 1 µF, Yageo RC0402 resistors, RK73H1ETTP4701F 4.7k, 2N7002-7-F, BAT54W,135, PESD5V0L1UL,315, SMF9.0A). New values exist only where the circuit needs them (dividers, R_ILM legs, ILIM, MID/CBSET, FB/EN).

## Removed from E0003
STUSB4500, BQ25798 + its support parts, BQ29209 + Q8–Q10 + its RCs, MID divider, TVS2200DRVR, PD_ALERT/P06 pull-ups, GP2 0R option.
