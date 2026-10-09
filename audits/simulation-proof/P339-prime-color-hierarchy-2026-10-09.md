# P3.39 — Prime carriers / derived color hierarchy
2026-10-09. User specification: Jane/pink, Patricia/purple, Toph/green, Icarium/blue are **prime**; divide by three and add secondary, tertiary and quaternary color layers.

Implementation convention, explicit rather than inferred: each of Patricia's 360-step hops has three 120-step sectors, with four hops totaling 1440 slots. Four prime identities remain immutable. The derived levels are RGB channel mixes between neighboring primes: secondary midpoint, tertiary midpoint of prime and secondary, quaternary midpoint of secondary and neighboring prime. Labels are categorical palette tiers and do not imply optical nonlinear harmonics or spectral wavelengths. RGB blending is not scientifically accurate photon-color mixing, and there is no automatic reason these exact mixes must correspond to traditional pigment secondaries.

The new P3.39 module and test have been committed. Regression source enumerates all 1440 slots x 4 carriers = 5760 carrier states, requiring lossless sector indexing, pinned scalar 0, preserved prime identities, valid derived colors and error handling. **Execution of the exact JavaScript test has not been verified in this turn; do not claim a runtime PASS.**

The division-by-three choice is currently temporal-sector decomposition. If /3 instead denotes recursive thirds of the color hierarchy rather than temporal subdivision, this branch remains an auditable implementation hypothesis and should be revised without changing the four primes.
