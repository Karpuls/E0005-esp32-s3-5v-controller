# E0005 rev A BOM

`E0005_revA_BOM.csv` is a copy of `bom/E0005_digikey_bom.csv`. `build/scripts/fab_export.sh` regenerates it from the schematic fields with `build/scripts/make_bom.py`, so never edit the CSV by hand: change the MPN tables in `build/scripts/gen_sch.py` and regenerate.

- **89 lines:**
  - 85 on-board lines: 268 references, of which **R60 is DNP**, so 267 fitted;
  - E0003's off-board lines: display, EYESPI cable, 2 cells.
- **Columns:** Supplier, Qty, QtyBasis (`schematic` or `spec`), References, Value, Footprint, MPN, Manufacturer, SupplierPN, Stock, Lifecycle, UnitEUR (or USD where marked), LeadWeeks, DNP, OwnerStock, Notes.
- **Data sources** (no BOM-wide API sweep; see `bom/notes.md`):
  - parts reused from E0003: stock, price and lead time copied from E0003's API-checked BOM (2026-10-18);
  - new parts: one DigiKey lookup each (2026-10-27, `bom/new_parts_digikey.csv`).
- **Common parts:** E0003's common MPNs wherever the value exists (100 nF GRM155R71H104KE14D, 10 µF TMK212BBJ106MG-T, 22 µF CL21A226KQCLRNC, 47 µF CL32A476KOJNNNE, Yageo RC0402 resistors, 2N7002-7-F, BAT54W, PESD5V0L1UL, SMF9.0A/SMF5.0A, AO3401A).

**Non-DigiKey lines:**
- SM04B-GHS-TB, LCSC C189895 (J1–J4);
- SM02B-GHS-TB, LCSC C189893 (J6–J9, J12): DigiKey had 0 stock for both;
- EYESPI cable, Adafruit 5239;
- 2 × Molicel P50B, nkon.nl / akkuteile.de.

**To confirm at order time:**
- U2 BQ25887RGER cut tape 296-53517-1-ND;
- U17 TPS56637RPAR cut-tape PN (the lookup returned only the T&R listing).

See [PREORDER.md](PREORDER.md).

`assembly/E0005_revA_BOM_JLC.csv` is the same on-board BOM in JLC's column format (fitted parts only), for a JLC assembly quote. It has MPNs but no LCSC numbers except the two GH connectors.
