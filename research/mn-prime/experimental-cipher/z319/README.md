# Z319 — RGB symbolic orientation tests

Date: 2026-10-18
Status: Layer 1 symbolic test; no claim of physical electron orbitals or discovery of Z319.
User orientation key Tun retained; letter-to-axis rule remains **unspecified**.

Baseline: RGB channel occupancy (3,1,2), sum 6. Independent structural register (1,2,1) unchanged.

Transforms:
- Rotate channels (r,g,b)->(b,r,g). 3 rotations restore original.
- Mirror channels (r,g,b)->(b,g,r). 2 mirrors restore original.
- Signed inversion (r,g,b)->(-r,-g,-b) expresses orientation sign only; negative counts are **not electron occupancies**.

Executed locally:
- Z318 test_rgb312.py: 8/8 PASS.
- Z319 test_orientation.py: 10/10 substantive assertions PASS.
All tests verify symbolic math only.

Invariants: rotations and reflections conserve the multiset {1,2,3} and sum 6; exactly six permutations. Signed inversion is modeled separately from counts.

Open: The actual geometry encoded by letters in 'Tun'; wavelength/color and electron physical quantum-number correspondence; mapping to V12 visual axes.

Frozen KET unchanged.
