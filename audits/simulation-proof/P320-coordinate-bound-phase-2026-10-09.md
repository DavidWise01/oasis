# P3.20 — Coordinate-bound Dyson dual-arm gate phase (2026-10-09)

Source: `docs/reality-tensor/dyson-inversions/p320_coordinate_binding.mjs`. Test: `test_p320.mjs`.

Parent dependencies are P3.18 typed hierarchy and P3.14 dual-arm gate compiler. The canonical address remains ten tokens `00 11 22 33 42 24 33 22 11 00` plus six-digit base-11 seed and typed dimension/quad/vogel/voxel/vector fields. Both arms retain their own captured complex amplitude.

## New binding law (stipulated, not experimentally derived)
`r = (seed + 11*dimensionIndex + 17*quadIndex + vogel + 3*voxel + 5*vector) mod 65521`, with exact bigint integer reduction before conversion to number. Phase `phi = 2*pi*r/65521`. Left arm gets `+phi`, right arm gets `-phi`, on top of the original per-gate angle. Inversion uses the unchanged full address and all three complex output channels, applying the adjoint operations in reverse sequence.

**Limits:** finite modulus necessarily creates phase collisions: different addresses may have identical phase; it is not a secure hash, authentication key, or uniqueness proof. The complete serialized address is preserved separately. Changing an address on a transported state will generally prevent faithful inversion, but that is not a cryptographic tamper detection guarantee. Removing a retained channel destroys full-state reversibility in general. `{{-211mv}}x10^-35` remains separately preserved and is not used to justify phase coefficients.

## Validation status
The test file defines 25,000 seeded randomized cases for norm conservation, full route and coordinate recovery, forward/inverse error thresholds, plus altered-address sensitivity. The source and test have been committed to GitHub. **The new test was not executed in this turn**, and neither local numerical results nor CI success should be inferred from source inspection alone.

## Next P3.21
Execute the exact committed JavaScript dependency tree; audit phase collisions across the million seeds; introduce optional append-only integrity commitments to detect altered addresses without treating the reversible phase map as cryptographic authentication.
