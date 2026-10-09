# ROOT0 P3.15 — Dual-arm apex schedule audit (2026-10-09)

Canonical two sides: `-+- /\\ +-+`. Parent implementation: `p314_dual_branch.mjs`. Three explicit schedules use the same ten address positions and both separate retained arm ports: left-first (20 gate events), right-first (20), and symmetric paired Strang convention L-half → R-full → L-half (30). The half gate uses half the mixing angle `asin(sqrt(eta))` and half the imposed phase, **not** half the capture probability.

Independent local Python complex-arithmetic implementation: 25,000 seeded randomized 3-channel states per schedule, 75,000 total. All passed inverse and energy-preservation tests. Maximum absolute component recovery error across schedules 3.756755865433588e-15; maximum norm discrepancy 8.881784197001252e-15.

Initial traveling amplitude 1, retained ports empty, normalized energy fractions:
- LR: [0.48198112010408467, 0.08162548196418054, 0.4363933979317344]
- RL: [0.48198112010408467, 0.4363933979317344, 0.08162548196418054]
- PAIRED: [0.46635904199315986, 0.2681340385119664, 0.2655069194948735]

LR-vs-RL output state Euclidean gap: 0.5950525123584774. All-zero vector remains fixed. A normalized nonzero input cannot collapse to all-zero under unitary operations; full inverse reconstitutes the original traveling state.

The executable repository JavaScript regression suite `test_p315.mjs` has been committed but could not be executed directly from the GitHub remote within the local container; GitHub raw hostname resolution failed. Remote CI remains unverified. Numerical results describe an independent local implementation of the stated gate equations, not measured physical dynamics.

Model scope: user notation does not fix the half-gate schedule or coupling values. No claim of physical Dyson energy conversion, negative-energy existence, or transit at Planck length. Voltage `{{-211mv}}x10^-35` is preserved as a separate wrapper, not a derived gate coupling.

P3.16 target: formalize apex boundary and simultaneous-time interpretation, determine whether symmetry requires arm-port exchange, phase conjugation or both, and test conditions under which final retained arm magnitudes exactly balance.
