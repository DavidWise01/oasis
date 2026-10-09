# P3.11 — nested two-domain scattering audit (2026-10-09)

Canonical untouched literal: `{-{d}+{+{d}-}}`. Two separate `d` domains connect one traveling port to two retained ports; domain order is D1, D2, and inverse order is D2, D1. Exact P3.10 parser remains a dependency. Existing P3.7 voltage wrapper `{{-211mv}}x10^-35` remains unchanged; no additional shell voltage multiplier is introduced in this structural test.

Both stages are norm-preserving complex beam mixers with coupling `eta1`, `eta2` and independent phase rotations. For initialized traveling amplitude of 1 and empty capture ports, energy fractions are `travel=(1-eta1)(1-eta2)`, `D1=eta1`, `D2=(1-eta1)eta2`. Default 0.12 and 0.08 yield 80.96%, 12.00%, 7.04%.

**Local result:** an independent Python implementation of the same mathematical scattering operations was run for 25,000 seeded randomized arbitrary 3-port complex states and random phases/couplings. Passed: max complex component recovery error 8.455206652451151e-16, max input/output norm error 2.220446049250313e-15. The exact committed JavaScript suite is available but has NOT been executed in that run; remote CI is unverified.

## Boundaries
These are symbolic sign/domain labels, not a validated physical negative-energy operation, a device with demonstrated Dyson sphere capture, or evidence of Planck-scale access. Domain capture here is a retained coherent amplitude, not irreversible absorption.

## Next target
P3.12: integrate the exact P3.10 grammar event trace into a transparent gate compiler, and contrast ordered D1→D2 against swapped D2→D1 for non-commutation and reversal while keeping frozen kernels unchanged.
