# Experiment 029 — PRIM address alignment

Canonical requested topology: `3 × 2(-+) × 2(Aa-Zz) × 2(01-11)`.
Preserve earlier spatial string literally: `{{ 1s8t1u8v 001w8x1y8z }}`.
Preserve primitive: `[-+{s1}{ns1}[(s3)]{ns2}{s2}-+]`.
Carrier: `[(n())]`.

Interpretation chosen for this test: 3 spatial axes, two polarities, 26 possible letter identities with 2 case modes, and 2 binary tags. 624 unique addresses (208 per axis); fixed-letter subregister has 24 states. Address encoding needs at least 10 bits (not 10 independent physical degrees). In-place polarity, case and binary toggles map addresses to valid addresses. Six-hop phase arithmetic: 6×0.3367−2×0.0101=2 cycles.

**Gaps added to alignment specification:** explicit letter identity, case as separate binary mode, unique compound address, axis addressing, boundary polarity, binary label preservation, inference carrier provenance, and physical-delay metadata as *unresolved*. Do not treat addresses as oscillators or derive propagation delays without spatial positions and a velocity.

**Not established:** axes coordinate mapping, physical connectivity, delay/rate distribution, independent reference sensing, dynamic synchronization across the 624 addresses or any CERN discovery. The previous seven-oscillator mirrored geometry is superseded as canonical by this three-register topology, but its numerical results remain results for its original toy topology.
