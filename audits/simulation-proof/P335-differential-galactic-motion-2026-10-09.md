# P3.35 — Differential Galactic Motion (2026-10-09)

Parent: P3.34. Preserve scalar-0 root and Patricia's independent 4×366 symbolic spinor slots.

Implement the demonstration rotation law `omega_matter(R) = (2π / 250,000,000 years) × (26000 ly / max(R,12000 ly))`. This supplies a flat outer circular-speed reference and a solid-body inner transition. The spiral **pattern**, not a material star, has illustrative period 320 million years, independent of the matter rotation; research has not established one universal pattern speed (see Griv et al., 2026, https://link.springer.com/article/10.1007/s10509-026-04594-0). The schematic does not replace detailed Gaia rotation-curve data.

Executed local Node test using exact source: PASS 41,464 checks comprising 10,000 positions for each of four samples plus 1,464 Patricia slot checks. Maximum radius preservation residual 1.4551915228366852e-11 ly. Fixed galactic reference origin remains [0,0,0]. Orbital time is in physical years; photon-spin ticks have no assumed conversion into elapsed years.

Limitations: the model uses circular planar orbits and omits radial migration, peculiar velocities, bar dynamics, vertical oscillations, and uncertainty propagation. No literal proof that a photon appears as a galaxy or is gravitationally trapped follows from symbolic morphology.

Next target P3.36: fit a radial velocity table with explicit data provenance; compare shearing star orbits against slower/faster spiral patterns, and test reversibility under time reversal.
