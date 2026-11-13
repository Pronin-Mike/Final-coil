# G01 wooden perimeter fence

Low-poly timber picket fence on the existing 1,000 m² G01 plot boundary. Approx. 1.45 m high; board bottoms follow the unchanged terrain. Chamfered board caps, five timber tones, posts at up to 2.4 m spacing, two rails per bay. Repeated geometry uses HISM components.

The 3.5 m driveway crosses the boundary obliquely: its projection along the fence is 8.57 m. The opening is therefore 9.6 m, preserving the complete existing road corridor plus clearance. Two braced leaves stand open at 90 degrees, one inward and the other outward, so neither cuts across the angled road. They are static blockout geometry; interaction is not implemented.

Source: Scripts/build_g01_fence.py. Placement and counts: fence_spec.json. Review: Review/G01Fence. The builder backs up the level before its first change and asserts that existing actors retain their transforms, including house, garage, bath and plot outline.

Validation: final PIE walking test passed all 9 waypoints: the driveway in both directions, on the centreline and at +/-1.1 m lateral offsets. No sticking or falls. Repository validation and git diff --check passed. Vehicle driving physics is not implemented/tested.
