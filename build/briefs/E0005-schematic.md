# E0005 Phase 2 subthread: schematic capture (rev A)

You own the **E0005 schematic** from an empty project to "ERC 0 + notes + DigiKey BOM". The E0005 lead thread launched you and is your only contact: report to it in your turn's final reply. You are the only writer of the schematic and project files during this phase. The lead owns `docs/SPEC.md`.

**Do not contact or involve any other bot** (no bot_send/room_*). Ask the owner nothing directly; if a real decision is needed, put it in your report to the lead.

## Project
- Folder: `/home/karpulis/KiCad/E0005 - ESP32-S3 5V controller` (git repo, remote `origin` = private `github.com/Karpuls/E0005-esp32-s3-5v-controller`, branch `main`). `.backplane.json` already points at `E0005_controller.kicad_pro`.
- Layout (exists): `docs/`, `lib/`, `bom/`, `build/` (git-ignored except `build/scripts/`), `fab/`, `mech/`. Datasheets already downloaded: `build/bq25887.pdf`, `build/tps56637.pdf`, `build/tps25947.pdf` (SLVSFC9C).
- **Input: `docs/SPEC.md` v1.0 (FROZEN).** Read all of it first. It defines every block, value, pin and reset state. If a datasheet forces a deviation, make the datasheet-correct choice, log it in `docs/schematic_notes.md` under "Deviations from SPEC v1.0" and list it in your report; do not edit SPEC.md.
- **Reference design: E0003** at `/home/karpulis/KiCad/E0003 - ESP32 control box mainboard` (reviewed, order-ready). Read its `README.md`, `docs/SPEC.md`, `docs/schematic_notes.md`, `bom/` (incl. `common_parts_across_projects.md`, `notes.md`, `sync_bom_digikey.py`) and its four sheets.

## Deliverables
1. **KiCad project** `E0005_controller.kicad_pro` / `.kicad_sch` (root) at the project root, **hierarchical sheets like E0003**:
   - `power.kicad_sch`: USB-C J11 (CC Rd + CC sense, USBLC6, SMF9.0A), U_IN TPS259470A with the 3-level R_ILM legs, BQ25887 charger, TPS56637 2S→5 V buck, soft power latch, TPS629210 3V3, V5_SENSE, V5 bulk.
   - `battery.kicad_sch`: holders/cells, F1, S-8252AAG + 2 × PSMN2R0-30YLDX + clamps, R_SENSE, MAX17205 (stack-only), NTC1/NTC2, reverse-cell LEDs. **No BQ29209, no Q10/BAL_EN, no OV2 FET, no MID→GPIO4 divider** (owner Q2).
   - `mcu.kicad_sch`: ESP32-S3-WROOM-1-N16R2 with the SPEC §7 pin map, BOOT/RESET, LEDs, TCA9535 (SPEC §5.10 map), EYESPI J10, switches J6–J9, power button + J12.
   - `ports.kicad_sch`: PCA9548A, 5 × TPS259470A port eFuses with the 5 V OVLO/UVLO dividers (SPEC §5.5), SMF5.0A, ESD + 220 Ω, J1–J5, "5V" port labels in the notes.
   Start from **copies** of the E0003 project files and sheets (never edit E0003 itself), then change what SPEC v1.0 §1.1 lists. Reuse E0003's symbols, footprints and libraries: copy `lib/E0003.kicad_sym`, `lib/E0003.pretty`, `lib/E0003_mech.pretty`, `lib/E0003_mech.3dshapes` into `lib/` renamed to `E0005*`, register them in `sym-lib-table`/`fp-lib-table` as `E0005` / `E0005_mech`, and rewrite the `E0003:` / `E0003_mech:` library references in the copied files consistently. Give new parts (BQ25887, TPS56637, P-FET, etc.) symbols/footprints from the standard KiCad libraries where they exist, otherwise with `kicad-symbol` / `kicad-footprint` into the E0005 libs.
2. **Schematic-phase checklist** (SPEC §11 and PlaceRoute's list), each closed in `docs/schematic_notes.md` with the datasheet reference:
   - **BQ25887 reference circuit** (datasheet §9.2): VBUS/PMID/SNS/BAT/REGN/BTST caps, 1 µH inductor, TS divider for the 103AT-2 (JEITA 0–60 °C), R_ILIM 374 Ω, PSEL pull-up, CD pull-up, MID 300 Ω, CBSET 39 Ω 2512, STAT/INT/PG; behaviour with CD high and no battery, and with the buck back-feed (BAT+ ≈ 4.3 V).
   - **TPS56637 FB and EN dividers**: V_OUT 4.80 V (FB 0.6 V); EN UVLO ≈ 5.4 V rising from BAT+ through the latch P-FET, including the 1 µA / 4 µA EN input and hysteresis currents; EN ≤ 5.5 V at 8.4 V; MODE to GND (Eco-mode); PG pull-up; output/input caps (V5 bulk 6 × 47 µF per SPEC §5.1.1).
   - **U_IN legs**: 6.65 kΩ base, 3.83 kΩ leg A (P06), 2.32 kΩ leg B (P07), 2N7002 legs with 100 k gate pull-downs; OVLO 1 M / 249 k, EN/UVLO 1 M / 390 k, ITIMER 22 nF, dVdt 1.8 nF, FLT → P15.
   - **Port eFuse dividers** at the corners (OVLO 1 M / 249 k, EN/UVLO 1 M / 365 k).
   - **CC sense**: 5.1 kΩ Rd, 10 kΩ + 1 nF to GPIO6/GPIO7; show the ADC readings stay inside the Type-C vRd windows including ADC leakage.
   - **Soft power latch**: P-FET (VDS ≥ 20 V, VGS ≥ ±12 V), gate network, PWR_HOLD N-FET from GPIO36, button via BAT54W, GPIO21 sensing; check VGS at 8.4 V and the behaviour with USB present.
   - **DigiKey stock for every new part** (BQ25887RGET, TPS56637RPAR, 1 µH inductor Isat ≥ 5 A, 39 Ω 2512 1 W, SMF5.0A, P-FET, any new passives). Use the pcbparts MCP `digikey_get_part` (shared daily quota: one call per part, no BOM-wide sweeps; reuse E0003's checked parts without re-querying). Prefer E0003's common parts for every passive value.
   - ESP32-S3 pin check for the changed pins (GPIO4/6/7 ADC1, GPIO36 PWR_HOLD, GPIO48 EXP_INT_N).
3. **ERC 0** (errors and warnings, or every remaining warning justified in the notes) with `kicad-cli sch erc`. Save the report in `build/`.
4. **`docs/schematic_notes.md`** in E0003's style: per sheet what was built and why, calculations, checklist results, deviations, open items.
5. **DigiKey BOM**: every symbol has `MPN`, `Manufacturer` and the DigiKey part number field used by E0003; `bom/E0005_digikey_bom.csv` in E0003's column format (generated from the schematic, never hand-edited for content), `bom/notes.md` with substitutions and stock exceptions.
6. **Placement note** `docs/placement_notes.md`: the SPEC §9 edge plan and **U_IN's cooling copper reservation from SPEC §5.6.1** (≈ 15 × 12 mm F.Cu keep area; IN and OUT pours ≥ 80 mm² each; ≥ 6 vias per pour ≥ 0.15 mm from pads to In2 V5 / B.Cu VBUS ≥ 100 mm²; GND pin ≥ 2 off-pad vias to In1; solid zone connection; ≥ 5 mm from BQ25887, both inductors and the TPS56637), plus the hot-loop/Kelvin notes for BQ25887, TPS56637 and R_SENSE.
7. **Commit and push** (`git push origin main`) at each milestone: project copied, each sheet captured, ERC 0, BOM done.

## How to work
- Follow the `kicad-schematic` skill: edit through the backplane `kicad_ipc` tool where it fits (BeginCommit/EndCommit, SaveDocument), or edit copied files directly and re-read them; render the sheets to PNG and look at them; check netlists deterministically; tidy layout, 50 mil labels, coloured net groups, boxes per subcircuit. Show the root schematic with `viewer_show` when it is saved.
- Keep the E0003 reference designators where the part is the same; renumber only new or removed parts.
- No test points (no TP symbols).

## Report to the lead when done
"Schematic ready for review" + ERC result, sheet list, the checklist outcomes with key values, BOM stock exceptions, deviations from SPEC v1.0, liberties taken, and the commit hash pushed.

## Owner house rules (permanent)
- No test points. Bring-up is through USB and component pads.
- No vias on or under pads (≥ 0.15 mm via-to-pad copper gap; EP thermal vias exempt).
- All tracks at multiples of 45°.
- DigiKey-preferred full BOM, common parts as defaults (see E0003 `bom/` common-parts list).
- JLC 4-layer impedance stackup (90 Ω USB pair), JLC design rules + no-via-on-pad rule in `.kicad_dru`.
- Commit at every milestone.

## Owner decision on placement and routing tools
Owner decision from PlaceRoute (final, overrides the brief's earlier tool wording; the brief file is updated): placement uses the KiStack `layout-placement` scripts. Routing is by hand or script via IPC only (`kicad-layout`). **No autorouters of any kind**: no TraceMaker, no Freerouting, no other autorouter, and don't load the `tracemaker` skill.

## Skills to use (KiStack, github.com/American-Embedded/kistack @641ade9, installed in ~/.claude/skills)
Load the skills that fit your job with the Skill tool before you start, and follow them:
- Placement: `layout-placement` (scripts: `~/.claude/skills/layout-placement/scripts/run.sh <script>.py ...`; uv is in ~/.local/bin) + `kicad-layout`
- Routing / cleanup: `kicad-layout`, by hand or script only. The owner allows no autorouters (no TraceMaker, Freerouting or any other).
- Review / QC: `kicad-pcb` (DRC, layer renders, 3D interference), `kicad-gerbers` for fab output review
- Exports (ERC/DRC reports, gerbers, drill, pos, BOM): `kicad-export`
- Parts/BOM: `kicad-bom`; footprints/symbols: `kicad-footprint` / `kicad-symbol`; schematic: `kicad-schematic`; panels: `kicad-panelize`; renders: `pcb-product-render`
If you start subthreads or delegate tasks yourself, copy this whole section into their brief so they use these skills too.

For this phase load at least `kicad-schematic`, `kicad-bom`, `kicad-symbol`, `kicad-footprint` and `kicad-export`.
