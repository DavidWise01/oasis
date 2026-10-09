# P3.18 — Complete typed hierarchy / million-seed routing
Date: 2026-10-09. Parent: P3.17, unchanged.
Canonical prefix: `00 11 22 33 42 24 33 22 11 00`. Six base-11 digits identify seeds in [0,999999]. Signed dimensions `-1+ -2+ -3+`, quads `Aa Bb Cc Dd`, followed by vogel/voxel/vector signed arbitrary-precision integer coordinates. Address encoding uses `|` separators as a serialization choice in this test only; this is not a change to prior HACI attachment semantics.

**Local Node executed:** 1,000,000 distinct seed states, complete encode/decode/inverse round trips and collision detection. PASS: zero collisions, zero mismatches. Three malformed input categories rejected. Example: `00.11.22.33.42.24.33.22.11.00/623350|-3+|Dd|-2|3|0`.
**Limitation:** one million distinct seeds are tested with deterministic associated metadata. This does not enumerate all combinations of dimensions, quads and infinite signed coordinates, though the formal serialization retains each valid tuple. The terms vogels, voxels and vectors are hierarchy labels, not a verified physical geometry.
The paired branches `-+- /\\ +-+` remain symbolic at this layer. This test does not demonstrate physical Dyson inversions or Stargate transit. Remote CI not verified.
Next target: P3.19 route both physical-model channels against this exact hierarchy, and verify that inverse scattering preserves the route key and all retained channels.
