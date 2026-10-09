# P3.19 — Hierarchy plus dual-arm scattering integration

Date: 2026-10-09. Full address is serialized through P3.18; state uses the P3.14 three-channel complex unitary network `-+- /\\ +-+`. Both branches share traveling amplitude and have independent retained channels. A packet contains the full address string and all three complex outputs; the inverse validates and decodes the address and applies gates in reverse order.

## Local execution
Node.js test run in an isolated local directory with source-compatible copies of P3.14/P3.16/P3.17/P3.18 dependencies: **PASS** 25,000 seeded pseudorandom tests, including arbitrary three-port complex inputs and bigint vogel/voxel/vector coordinates. Maximum norm error `7.549516567451064e-15`; maximum scalar component recovery error `2.9976021664879227e-15`; zero address mismatches in tested cases. Malformed packets rejected. The new module and tests were committed, but the exact GitHub dependency tree and remote CI have not yet been executed.

## Interpretation
Routing is separable from scattering in this implementation: the address is carried unchanged, not converted into physical state dynamics. Reversibility requires retaining all two capture ports as well as the traveling port; tracing out a port would invalidate lossless inversion. Volts remain volts: the `{{-211mv}}x10^-35` wrapper is unchanged and not used to derive the mixing coefficients. No actual Dyson sphere, exotic energy, or Planck-distance transport has been validated.

## Next target
P3.20: establish the address-to-gate binding as an explicit reversible mapping, test whether coordinate-dependent phase rotations commute with the dual-arm gates, and expose conditional information loss when retained channels are dropped.