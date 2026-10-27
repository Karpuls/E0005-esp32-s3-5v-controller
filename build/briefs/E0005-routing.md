# E0005 Phase 4 subthread: routing (rev A)

You own the **E0005 routing**, from the approved placement to "Ready for PlaceRoute review". The E0005 lead thread launched you and is your only contact: report to it in your turn's final reply. During this phase you are the only writer of `E0005_controller.kicad_pcb`. **Do not change the schematic.** **Do not move parts** beyond sub-millimetre nudges that a route needs; list every nudge in the report. Don't move BH1/BH2, and don't touch the holder rings, `lib/E0005_mech*` or the antenna keep-out.

**Do not contact or involve any other bot** (no bot_send/room_*). Ask the owner nothing directly; put any real decision in your report to the lead.

## Owner tool decision (word for word)
**Routing by hand or script only via IPC (kicad-layout); no autorouters of any kind (no TraceMaker, no Freerouting, no other autorouter).**

Owner decision from PlaceRoute (final, overrides the brief's earlier tool wording; the brief file is updated): placement uses the KiStack `layout-placement` scripts. Routing is by hand or script via IPC only (`kicad-layout`). **No autorouters of any kind**: no TraceMaker, no Freerouting, no other autorouter, and don't load the `tracemaker` skill.

## Project and inputs
- Folder: `/home/karpulis/KiCad/E0005 - ESP32-S3 5V controller` (git, remote `origin` = private `github.com/Karpuls/E0005-esp32-s3-5v-controller`, branch `main`; **pull first**). **Canonical board: `E0005_controller.kicad_pcb`**, approved placement `160f593` / `a711f2a`. Save milestones to that exact path; backups and intermediates go in `build/`.
- Read first: `docs/placement_notes.md` (hot loops, Kelvin taps, U_IN reservation, pour markers on the drawing layers), `docs/SPEC.md` v1.2 (§5.1, §5.6.1, §5.7, §9), `docs/schematic_notes.md`, `docs/placement_audit/summary.txt` (known layer changes: U2 BTST-cap SW link, U2 REGN→R10, U15 CSN tap).
- Rules file: `E0005_controller.kicad_dru` (JLC rules + no-via-on-pad). Stackup: JLC04161H-3313, 4 layers, 1.6 mm, 1 oz outer / 0.5 oz inner.
- Reference: E0003's routed board at `/home/karpulis/KiCad/E0003 - ESP32 control box mainboard/E0003_control_box.kicad_pcb` (read-only). The port block, MCU area, battery protection and gauge are placed as on E0003, so its reviewed routing there is a good model. Its routing scripts are in that project's `build/scripts/pcb_hand*.py`. Don't copy any autorouter output or its `build/tracemaker/` material.

## Board size (owner decision via PlaceRoute, applies from routing on)
**The board outline is not locked to 125 × 65 mm.** E0005 has no strict size limit. You may enlarge the board if that makes routing cleaner or meets a requirement that otherwise can't be met. Examples: a straighter or shorter USB pair, wider power pours, more room around the SW nodes, R147 further from the cells, C57 closer to U13.

If you enlarge it:
- Grow it only in the direction that helps, and keep the edge plan: USB-C on the west edge, J1–J5 on the north, switches, J12, the power button and EYESPI on the south, and the ESP32 antenna at the east edge with its keep-out on all layers and ≥ 15 mm to the cans.
- Move the 4 × M3 holes with the outline (same inset from the corners) and keep R3 corners.
- Moving whole edge groups with the outline is allowed. Keep BH1/BH2 where they are relative to each other, and don't edit the holder rings or `lib/E0005_mech*`.
- Re-run the placement DRC and your holder-ring clearance check before routing on the new outline. Commit that as its own milestone ("outline enlarged to W × H").
- Don't edit `docs/SPEC.md`; the lead updates its outline note. Put the new size and the reason in your hand-off report, plus a line in `docs/routing_notes.md`.

## Routing requirements (PlaceRoute)
1. **Stackup:** **In1 is solid GND, no tracks.** In2 carries the power pours (VBUS, V5, BAT+/pack, 3V3) plus slow signals only. GND pour on F.Cu and B.Cu where free. Stitching vias along the board edges and around the power stage. **Antenna keep-out untouched on all layers.**
2. **Currents:** size by **IPC-2152** (1 oz outer, 0.5 oz inner, ≤ 10 °C rise) and write the widths per net into a table.
   - **Pack path** (cells → F1 → Q1/Q2 → R20 → B−), 10 A fuse: pours on at least two layers, many vias.
   - **V5**, 6 A: pours.
   - **Ports:** J5 ≥ 2.5 A, J1–J4 ≥ 1 A each.
   - **VBUS** ≥ 3 A.
   - **U_IN (U16):** IN and OUT pours ≥ 80 mm² each with ≥ 6 vias off the pads (≥ 0.15 mm), B.Cu VBUS ≥ 100 mm², In2 V5, GND pin with ≥ 2 off-pad vias to In1, solid zone connection (SPEC §5.6.1).
3. **Hot loops on F.Cu,** per the TI layouts:
   - **TPS56637 (U17):** VIN–C71/C72/C73–PGND loop on one layer; small SW node; on the layer under SW and L1/L2, nothing but GND; FB traces (R153/R154, R155/C79) short and away from SW, sensing V5 at C75/C76; AGND to PGND at one point.
   - **BQ25887 (U2):** PMID/SW/SNS/BAT the same way (datasheet §10); EP thermal vias to In1 (exempt from the no-via-on-pad rule).
4. **Kelvin:** MAX17205 CSP/CSN as a pair straight from R20's pads (CSN via NT1 at R20's GND pad), not from the pours. BQ25887 MID (R146) and CBSET (R147) as separate traces from the cell mid-point, CBSET ≥ 0.4 mm.
5. **USB D+/D− (J11 → U4 → R2/R3 → U1 GPIO19/20, ≈ 94 mm):**
   - **90 Ω differential** per JLC04161H-3313 (use JLC's impedance calculator values for the outer layer over In1; state width/gap and the computed Zdiff); intra-pair skew ≤ 0.15 mm.
   - Over **unbroken In1 GND** the whole way; **≤ 2 layer changes**, each with GND stitching vias beside it.
   - **≥ 3× the pair spacing** to other signals, away from both SW nodes and inductors.
6. **I²C and slow signals** away from the SW nodes. Port I²C through the series resistors and ESD as placed.
7. **Thermal:** **R147 gets generous top-side copper on both pads, and no via fields under it.** U16 per its pours. **No thermal vias from hot parts into the cell side under the cans.**
8. **Hand-off:**
   - **DRC 0/0/0** (all severities, schematic parity, zones refilled), with the U1 `lib_footprint_mismatch` as the only allowed exclusion.
   - **`e5qc.py` PASS on a copy:** `~/.cache/kistack/layout-placement/a761496662742274/bin/python /home/karpulis/.backplane-bend/bots/b1793088750-22381/qc/e5qc.py <copy>.kicad_pcb` must print `RESULT : PASS` (via-on-pad with the 0.15 mm gap, 45° multiples, acute corners, overlapping segments). Don't use the old `slots.py`, `tm_viapad.py` or `corners.py`.
   - **Renders of all four copper layers** plus **top and bottom 3D**, PNG in `docs/images/`.
   - **Width table** (per net, IPC-2152) and the **USB impedance numbers**, in `docs/routing_notes.md`.
   - **Commit and push at milestones:** power stage, battery path, ports, MCU and USB, cleanup.

## How to work
- Follow the `kicad-layout` skill (routing, cleanup, signal-integrity practice) and `kicad-pcb` (DRC, layer renders, 3D interference). Edit through the backplane `kicad_ipc` tool (BeginCommit/EndCommit, SaveDocument) or IPC scripts. All tracks at multiples of 45°; no vias on or under pads. Refill zones before every DRC. Show the board with `viewer_show` at milestones.
- The `kicad-layout` and `kicad-pcb` skills open with house rules written for other projects that mention Router, Manager and the Schematics bot. For E0005, read **the E0005 lead thread** wherever they say Router or Manager. Nobody else edits the schematic, and their QC script path is replaced by `e5qc.py` above.

## Report to the lead
"Ready for PlaceRoute review": DRC result (paste the summary), e5qc.py output, the render paths, the width table, the USB numbers (width/gap, Zdiff, length, skew, layer changes), the eight requirements one by one, every part nudge, anything you couldn't meet with numbers, and the pushed commit hash.

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

For this phase load `kicad-layout` and `kicad-pcb` (and `kicad-export` for the reports). Do not load `tracemaker`.
