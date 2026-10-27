# E0005 Phase 3 subthread: component placement (rev A) — PLACEMENT ONLY, NO ROUTING

You own the **E0005 board placement**, from an empty board to "Placement ready for review". The E0005 lead thread launched you and is your only contact: report to it in your turn's final reply. During this phase you are the only writer of `E0005_controller.kicad_pcb`. **Do not change the schematic.** If a pin swap or schematic change would help, propose it in your report.

**Do not contact or involve any other bot** (no bot_send/room_*). Ask the owner nothing directly; put any real decision in your report to the lead.

## Owner decision on tools (word for word)
Owner decision from PlaceRoute (final, overrides the brief's earlier tool wording; the brief file is updated): placement uses the KiStack `layout-placement` scripts. Routing is by hand or script via IPC only (`kicad-layout`). **No autorouters of any kind**: no TraceMaker, no Freerouting, no other autorouter, and don't load the `tracemaker` skill.

In short: placement with the KiStack layout-placement scripts; routing by hand or script only; no autorouters of any kind. **This phase is placement only. Draw no tracks, vias or zones, except the keep-out zones, the board outline and the reserved-area markers named below.**

## Project and inputs
- Folder: `/home/karpulis/KiCad/E0005 - ESP32-S3 5V controller` (git, remote `origin` = private `github.com/Karpuls/E0005-esp32-s3-5v-controller`, branch `main`; pull first). **Canonical board: `E0005_controller.kicad_pcb`** (configured in `.backplane.json` via `E0005_controller.kicad_pro`). Keep that exact path, save milestones to it, and keep backups/intermediates in `build/`.
- Schematic (approved, frozen): `E0005_controller.kicad_sch` + `power/battery/mcu/ports.kicad_sch`, commit 9b1a340 or later. **SPEC v1.2**: `docs/SPEC.md` (§5.1.1, §5.6.1, §5.7, §9). **Read `docs/placement_notes.md` first and follow it**; it lists the references, hot loops, Kelvin taps and the U_IN reservation.
- Libraries: `lib/E0005*` (copied from E0003), `fp-lib-table`, `E0005_controller.kicad_dru` (JLC rules + no-via-on-pad; check it is in place).
- Reference board: E0003 at `/home/karpulis/KiCad/E0003 - ESP32 control box mainboard/E0003_control_box.kicad_pcb` (reviewed placement, same outline, holders and edge plan; read-only). **Reuse its outline (`E0005_mech:E0003_Outline_125x65_4xM3`), M3 hole positions, Keystone 1121 positions and its stackup/board setup** (4 layers, 1.6 mm, **JLC04161H-3313**, 90 Ω USB pair). Reused parts with the same reference and footprint may start from E0003's positions, but check every one against E0005's circuit. The power stage is new.

## Steps
1. **Update the board from the schematic** (all footprints in, nets right, no parity errors). The board does not exist yet: create it with the project's settings, board setup and stackup taken from E0003.
2. Place with the `layout-placement` skill and its scripts (`~/.claude/skills/layout-placement/scripts/run.sh <script>.py ...`; uv is in ~/.local/bin), following that skill: fixed parts first (outline, holes, holders, edge connectors, module), then IC orientation, decoupling, regulator/clock/RF/filter parts. Edit through the backplane `kicad_ipc` tool (BeginCommit/EndCommit, SaveDocument), or as the skill's scripts do. Show the board with `viewer_show` at milestones.
3. Run the skill's **placement audit and routability reports**, and DRC (`kicad-cli pcb drc`, all severities, schematic parity) for the placement-only checks.
4. Renders: top, bottom (`kicad-cli pcb render` / layer exports) and a 3D view, as PNG in `docs/images/` or `build/`.
5. **Commit and push** at milestones: board created, fixed parts placed, power stage placed, all placed, audit clean.

## What PlaceRoute checks at the placement review (each must be met and shown in the report)
1. **Board and edges:** E0003 outline and edge plan. **USB-C J11 on the west edge**; **J1–J5 on the north edge with "5V" silkscreen** (+ port number and "E0001"/"E0002") at each port; **switches J6–J9, J12, the power button SW and EYESPI J10 on the south edge**. **Keystone 1121 holders BH1/BH2 on the bottom at E0003's positions, with polarity marks** (+/− on both sides).
2. **Antenna:** the ESP32-S3 antenna at the east edge, over the board edge or in a keep-out (rule area: no copper on any layer under or beside it, per Espressif's module guidelines), and **≥ 15 mm from the antenna to the nearest cell can**. Measure and report the distance.
3. **U_IN (U16):** **15 × 12 mm keep area reserved** (with its passives C65, R133–R141, C66, C67, Q11, Q12). Leave room for the **≥ 80 mm² IN (VBUS) and OUT (V5) F.Cu pours** with **≥ 6 vias per pour off the pads** (≥ 0.15 mm), plus a B.Cu VBUS area ≥ 100 mm² and an In2 V5 connection. **≥ 5 mm from U2, L2, L1 and U17.** Mark the pour areas (e.g. User.Drawings/Cmts) so routing can't miss them.
4. **Hot loops:**
   - TPS56637 (U17): input caps C71/C72/C73 to VIN–PGND, tight, same layer; short SW–L1 node; C74 BOOT at pins 7–6.
   - BQ25887 (U2): PMID/VBUS caps (C8/C9, C2), SW–L2, and the SNS/BAT caps (C69/C70, C18) per datasheet §10.
   - **L1 with C75/C76 inside the ≈ 10 × 10 mm area** next to U17's SW pin.
   - **The 39 Ω 1 W CBSET resistor R147 spaced from heat-sensitive parts and from the NTCs (RT1/RT2)**; give your spacing.
   - FB/feed-forward (R153/R154, R155/C79) at FB.
5. **Battery side:** S-8252 (U6), protection FETs Q1/Q2, the 5 mΩ R_SENSE (R20) and fuse F1 grouped near the holders on a short high-current path. **Kelvin access for the MAX17205 (U15) CSP/CSN taps** at R20's pads.
6. **Ports:** each port's eFuse (U10–U14), SMF5.0A TVS and TPD2E2U06 ESD **within a few mm of its connector**; the I²C mux PCA9548A (U8) central to J1–J5.
7. **Decoupling and USB:** decoupling at every IC power pin; ESP32 bulk cap at the module. The USB ESD (U4 USBLC6) at J11, with a **short, straight 90 Ω path to the module** (GPIO19/20).
8. **DRC:** placement-only DRC clean (courtyards, edge clearance, silkscreen, parity), no via-on-pad violations; **the layout-placement audit and routability reports attached**. For the via-on-pad and corner checks you may also run the lead's QC scripts on a **copy** of the board: `~/.cache/kistack/layout-placement/a761496662742274/bin/python /home/karpulis/.backplane-bend/bots/b1793088750-22381/qc/<slots.py|tm_viapad.py|corners.py> <board copy>`.

## Report to the lead
"Placement ready for review": the board image paths (top, bottom, 3D), DRC result, the audit and routability output (paste the summaries, give the file paths), the eight checklist items one by one with measurements (antenna-to-can distance, U_IN keep-area size and clearances, hot-loop distances, port part distances, R147 spacing), anything you couldn't meet and why, proposed schematic or pin-swap changes, and the commit hash pushed.

## Owner house rules (permanent)
- No test points. Bring-up is through USB and component pads.
- No vias on or under pads (≥ 0.15 mm via-to-pad copper gap; EP thermal vias exempt).
- All tracks at multiples of 45°.
- DigiKey-preferred full BOM, common parts as defaults (see E0003 `bom/` common-parts list).
- JLC 4-layer impedance stackup (90 Ω USB pair), JLC design rules + no-via-on-pad rule in `.kicad_dru`.
- Commit at every milestone.

## Skills to use (KiStack, github.com/American-Embedded/kistack @641ade9, installed in ~/.claude/skills)
Load the skills that fit your job with the Skill tool before you start, and follow them:
- Placement: `layout-placement` (scripts: `~/.claude/skills/layout-placement/scripts/run.sh <script>.py ...`; uv is in ~/.local/bin) + `kicad-layout`
- Routing / cleanup: `kicad-layout`, by hand or script only. The owner allows no autorouters (no TraceMaker, Freerouting or any other).
- Review / QC: `kicad-pcb` (DRC, layer renders, 3D interference), `kicad-gerbers` for fab output review
- Exports (ERC/DRC reports, gerbers, drill, pos, BOM): `kicad-export`
- Parts/BOM: `kicad-bom`; footprints/symbols: `kicad-footprint` / `kicad-symbol`; schematic: `kicad-schematic`; panels: `kicad-panelize`; renders: `pcb-product-render`
If you start subthreads or delegate tasks yourself, copy this whole section into their brief so they use these skills too.

For this phase load `layout-placement`, `kicad-layout` and `kicad-pcb`. The `kicad-layout` and `kicad-pcb` skills open with house rules written for other projects that mention Router, Manager and the Schematics bot. For E0005, read **the E0005 lead thread** wherever they say Router or Manager. Nobody else edits the schematic, and their QC script path is replaced by the `qc/` path above.
