# Natural Bound 10 — Invariant zero / inward Planck-scale corridor (2026-10-27)

Evidence ID: ITD_BOUND10_INVARIANT_ZERO_PLANCK_CORRIDOR_20261027.

Status: CODATA_2022_LP_VERIFIED / SGR_A_MASS_DISTANCE_VERIFIED / SCHWARZSCHILD_ANCHORS_CALCULATED / NEW_729_LOG_REGISTRY / INVARIANT_SCALE_LIMITS_EXPLICIT / 24_FACTORIAL_CYCLE_PRESERVED / EARLIER_BOUNDS_UNMODIFIED.

This is an **append-only** child of [Bound 09](BOUND09_NATURAL_BOUND_2026-10-27.md). Do not replace, rename, or reinterpret the previous 729 **linear** stations: the new 729 **logarithmic scale** positions are a different numerical grid, sharing an address format, not an observed star census.

## Correct the approximate number

The proposed "1.61658-ish" is a close estimate of the **Planck length**. The latest CODATA 2022 value (available in 2026) is

    l_P = 1.616255(18) × 10^-35 meters
    t_P = 5.391247(60) × 10^-44 seconds

Reference: NIST CODATA 2022 constants, https://physics.nist.gov/cuu/pdf/all.pdf . The parenthesized last digits denote one-standard-deviation uncertainty. Neither value is a demonstrated finite lattice size or the measured size of Sagittarius A*'s inner core. These constants follow from hbar, G, and c; l_P = sqrt(hbar*G/c^3).

## The exact 000 → 001 invariant-zero distinction

Three different concepts **must not be conflated**:

- **000 — r = 0**: formal mathematical center of a spherically symmetric Schwarzschild geometry. The metric predicts a singularity there; no physically measured endpoint or valid finite force is assigned.
- **001 — r = l_P**: nonzero Planck reference scale. Not a measured surface, a core, an event horizon or a guaranteed minimum physical length.
- **728 — r = R0 = 8,277 pc**: adopted Sun–Galactic-Center distance, observationally constrained by Sgr A* stellar orbits.

In spherical symmetry, define the geometric **areal radius** by r = sqrt(A/(4π)), where A is the area of a symmetry two-sphere. This r is invariant under simple radial coordinate relabeling; it is not an invariant spacelike route that remains valid across the horizon into the classical singularity. The dimensionless **zero-limit** zeta = r/R0 approaches zero mathematically as r approaches zero. At r=l_P it is nonzero.

We can therefore label a **Planck-reference path** without claiming to have solved the unobserved physical black-hole interior.

## 729 inward resolution levels, deliberately logarithmic

    label 000:             mathematical center sentinel: r=0
    label 001:             r = l_P
    labels 002 ... 727:   exponential increase in r
    label 728:             r = 8,277 parsecs (Sun)

    r(i) = l_P * (R0/l_P)^((i-1)/727),    1 <= i <= 728

    log10(R0/l_P) = 55.19871361900953 decades
    one log step   = 0.07592670374004062 decades
    scale factor   = 1.1910409780351636 per outward level

The index order outward is 000→001→...→728; moving inward from the Sun is 728→727→...→001→000. **Do not** equate index increment with physical time, a free-fall step, a star, or a propagation signal.

The new grid's 000–728 addresses also map into the earlier 24! permutation traversal via rank % 729, with rank 000 → Gray 000, rank 001 → Gray 001 and the final logical ring seam 728→000. That ring topology describes **computer state**, not the topology of spacetime.

## Physically anchored central scales

Use the published 2022 GRAVITY Sgr A* mass = 4.297 million solar masses and distance R0 = 8277 pc, https://doi.org/10.1051/0004-6361/202142465 .

For a deliberately idealized **nonrotating, spherically symmetric Schwarzschild black hole**,

    r_s       = 2GM/c²          = 1.2690115577002773 × 10^10 m
                                ≈ 12.6901156 million km
    r_photon  = 1.5 r_s         = 1.903517336550416 × 10^10 m
    r_ISCO    = 3 r_s           = 3.8070346731008316 × 10^10 m

    K         = R_abcd R^abcd   = 12 r_s²/r^6    [m^-4]
    K l_P^4   = 1               => r ≈ 2.2561016048275532 × 10^-20 m

**The formal curvature criterion occurs far above l_P and deep inside the horizon**, around ~1.396 quadrillion Planck lengths from zero in the purely areal-radius formula. It is an algebraic extrapolation of **classical** Schwarzschild curvature to a domain where that model is not trustworthy. It is **not** a measured transition surface, a quantum gravity prediction, or a physical wall.

| Boundary | Exact scale, approximately | Fractional log-station index | Regime |
| --- | ---: | ---: | --- |
| Mathematical center | 0 m | 000 | sentinel only |
| Planck reference | 1.616255e-35 m | 001 | formal/unverified interior |
| Classical K*l_P^4=1 | 2.2561e-20 m | 200.47 | algebraic curvature threshold |
| Schwarzschild horizon | 1.2690e10 m | 592.29 | analytic horizon, **not** a curvature singularity |
| Photon sphere | 1.9035e10 m | 594.61 | Schwarzschild photon circular orbit |
| Schwarzschild ISCO | 3.8070e10 m | 598.58 | Schwarzschild massive-particle circular-orbit boundary |
| Solar reference | 2.5540153342e20 m | 728 | adopted galactic observational distance |

All fractional indices are **interpolations**. The actual horizon is not asserted to coincide with registry station 592; in this log grid station 592 lies just inside it and 593 just outside it.

### Exterior proper radial distance—not a unique universal center path

On the **static Schwarzschild t=constant exterior slice only** and for r>=r_s, the proper radial length from horizon to a selected sphere is

    L(r) = sqrt(r*(r-r_s)) + r_s*arcosh(sqrt(r/r_s)).

It is zero at r=r_s and real for r>=r_s. **This path length depends on a chosen spatial slicing** and cannot be extrapolated as the same physical static radial path inside the horizon. In particular **r=0 is not zero proper distance from the horizon**, so that definition cannot be used to "prove" a physical Planck-size center.

A freely falling observer has a proper-time trajectory across an idealized horizon; that requires explicit initial conditions and a separate treatment, not a straight Euclidean distance path or a global static reference frame.

The **common train boost** in Bound 09 cancels from separations. It does not rescale the center distance, horizon, curvature invariant or Planck length.

## Actual implemented artifacts

- [Stand-alone interactive logarithmic inward viewer and 24! Gray ring](bound10-invariant-zero.html).
- [Pure JS scale/curvature/exterior-slice engine](bound10_invariant_zero_core.js).
- [729 data levels with explicit unobservable interior flags](BOUND10_729_LOG_AREAL_RADIUS_20261027.csv).
- [Seven separate exact analytic/observational anchor entries](BOUND10_EXPLICIT_ANCHORS_20261027.csv).
- [Machine-readable source and verification receipt](BOUND10_INVARIANT_ZERO_AUDIT_20261027.json).

## Executed calculations, reproducibility and limits

The exact committed core was read back and executed. All **729** positions were verified to order strictly outward with valid inverse interpolation; station 000 remains a zero sentinel, 001 the CODATA reference, and 728 the solar radius. The derived r_s, photon sphere, ISCO, log-station horizon position and K*l_P^4=1 radius were computed from the declared constants. The exterior proper-distance function correctly rejects interior radii.

Both the 24! core and the new scale core execute their self-tests inside the HTML. The HTML's three inline scripts were separately syntax checked. A mock-browser DOM interaction test exercised Sun, horizon vicinity, curvature reference, Planck, center, Gray 000→001, last-to-first seam, reverse seam and invalid factorial-rank guard, all passing.

**Unverified:** real-browser screenshot/rendering, GitHub Pages publishing on the public URL, actual quantum-gravitational physics at or within l_P, an invariant center-traversing spatial geodesic, Kerr spin and metric, or the source Galactic potential away from its calibration radius.

## Next natural Bound 11

Choose a **physical worldline with clear initial conditions** (for example freely falling radial test particle from rest at infinity in the nonrotating Schwarzschild idealization). Parameterize its elapsed *proper time* by the areal radius and evaluate curvature, redshift/tidal reference marks and the horizon crossing. The classical trajectory should be **terminated/marked unreliable** before claiming physical predictions at Planck curvature. Keep logical 24! ring address independent of actual elapsed time and retain the seven prior physical boundaries as witnesses, not votes or quorums.
