# E0005 routing notes

## Outline
- **Outline enlarged to 125 × 73 mm** (was 125 × 65) during routing, 2026-10-27, with the owner's OK. The 8 mm was added at the
  **north** edge: the J1–J5 port band (connectors, eFuses U10–U14 and their passives, Q3/Q5/Q7) and the U16 USB-input stage moved
  north with the edge; everything else, including BH1/BH2, U1 and the antenna keep-out, stayed put.
  Reason: the band between U8/U9 and the port eFuses was full on all three routing layers (only one free 0.15 mm lane on B.Cu across
  x 18–36), so the U9/U8 fan-out, I2C0, the port FLT/OFF/I2C lines and SW1..4_IN could not be routed cleanly.
- The 4 × M3 holes keep their 4 mm corner inset: OUT1 now uses `lib/E0005_board.pretty/Holes_4xM3_125x73` (same 3.2 / 6.0 mm plated
  holes as `E0005_mech:E0003_Holes_4xM3`, which is left unchanged). Corners stay R3.
- Part nudge for the move: Q3 +0.3 x / −0.3 y (clear of the BH1 peg ring).
