# G01 — low-poly banya

A 6 × 5 m log cabin placed in the marked corner of G01, plot-local centre (10, -10.5) m. The courtyard-facing entrance leads to a washing/shower room, then through a separate doorway to the steam room.

Steam room: two-tier L-shaped timber benches (45 / 90 cm above floor), stove with stone charge, chimney and bucket. Shower room: tray, drain, mixer and overhead head, bench and hooks. Outside: three entrance steps and a small firewood shelter.

Clear door openings: 1.2 × 2.1 m; ceiling clearance: 2.5 m. Foundation follows the sampled terrain height; no terrain, existing buildings or plot boundaries were moved. Doors are fixed open placeholders. Heating, water and door interaction are not implemented.

Source: build_g01_banya.py; placement and dimensions: bath_spec.json. Run the build through Unreal Python with the map released by other editors. Review captures are in Review/G01Banya. check_g01_banya_play.py drives an actual PIE character through the entrance, both rooms and shower tray and back outside; capture_g01_banya.py captures the current level through MCP.

Validation: actual PIE walking passed all 23 route points after the final foundation adjustment. The test covered the three entrance steps in both directions, both doorways, the shower tray and circulation beside the steam benches/stove. Repository verification and git diff --check passed.
