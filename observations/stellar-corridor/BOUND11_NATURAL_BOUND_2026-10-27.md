# Natural Bound 11 - Invariant radial free-fall proper time (2026-10-27)

Record: ITD_BOUND11_TIMELIKE_INVARIANT_FALL_20261027

State: **APPEND-ONLY** / CALCULATED_E1_TIMELIKE_WORLDLINE / HORIZON_PROPER_TIME_FINITE / STOP_AT_KRETSCHMANN_BOUND / 729_UNKNOWN_FLAGS / 24_FACTORIAL_STATE_SEPARATE.

This is the successor of [Bound 10: Planck reference and mathematical zero](BOUND10_NATURAL_BOUND_2026-10-27.md), not an edit or replacement. Prior 729 linear Galactic field stations and observational discrepancies are unchanged.

## Natural physical boundary

Instead of treating the Sun-to-center straight line as the trajectory of physical stars or a fixed proper spatial path through an event horizon, define one radial timelike geodesic of a **test observer** in a **Schwarzschild** idealization of Sagittarius A*.

**Initial condition:** conserved specific geodesic energy E = 1, corresponding to a body released from rest **at infinity**. We begin timing the sampled segment at 100 Schwarzschild radii; it has nonzero inward motion at that point. It is not a release from rest at 100 r_s.

Observer's invariant proper time (its idealized onboard clock):

    dr/dtau = -c sqrt(r_s/r)
    T(r) = (2 r_s / (3 c)) * (r/r_s)^(3/2)
    tau_elapsed(r_start -> r) = T(r_start)-T(r)

T(r) is the remaining *formal* classical proper-time function to r=0, and its use beyond the declared curvature boundary is forbidden as a physical prediction. These equations are the E=1 Schwarzschild geodesic, **not** the galactic-scale Newtonian rotation model.

### Observational anchors and GR derivation

- Sgr A* mass M = 4.297 million solar masses (GRAVITY Collaboration 2022), https://doi.org/10.1051/0004-6361/202142465 .
- NIST CODATA 2022 Planck length 1.616255(18)e-35 m: https://physics.nist.gov/cuu/pdf/all.pdf .
- University of Edinburgh, John Peacock, General Relativity (2020–2021), section 15.1.3, equations 342 and 343, PDF page 72, https://www.roe.ac.uk/japwww/teaching/gr/GR_notes_2021.pdf .
- These are public theory/measurement references; no real infalling astronaut or particle trajectory at Sagittarius A* has been tracked through the horizon.

## Computed worldline

    r_s = 2GM/c^2 = 1.2690115577002773e10 m
    r_start = 100*r_s = 1.2690115577002773e12 m (~8.483 AU)
    tau(start -> horizon) = 28191.55968988335 s (7.8309888 h)
    tau(horizon -> classical r=0) = 28.2197794693527 s [FORMAL]
    K = 12*r_s^2/r^6
    K*lp^4=1 => r_stop = 2.2561016048275532e-20 m
    formal remaining time at r_stop to mathematical r=0
      = 6.689493420803197e-44 seconds = 1.2408064788027995 Planck times.

**A mass-independent algebraic identity:**

    r_stop^6 = 12*r_s^2*lp^4
    T(r_stop) = (2 r_s/(3c))*(r_stop/r_s)^(3/2)
              = (2/3)*(12)^(1/4)*lp/c
              = (2/3)*(12)^(1/4)*t_P.

The gravitational mass cancels only because we chose exactly this E=1 radial geodesic and the criterion K*lp^4=1. This ratio is **not** a measured physical lifetime, a quantum-gravity theorem, or proof the center has a Planck-scale size. The true trajectory cannot be extrapolated across a quantum-gravity regime with confidence.

### Free-fall curvature and tidal reference

For a Schwarzschild radial freely falling orthonormal frame, the ideal geodesic-deviation coefficients for a small separation are

    radial stretching:         +c^2*r_s/r^3 [s^-2]
    transverse compression:    -c^2*r_s/(2 r^3) [s^-2].

At r=r_s, radial coefficient ~= 5.580977e-4 s^-2. These are tidal **relative** accelerations per unit separation, not the observer's locally measured velocity or its proper 4-acceleration. An ideal geodesic observer has zero proper 4-acceleration.

The coordinate derivative dr/dtau can exceed c numerically inside the horizon. This does not indicate superluminal motion: r is areal radius, not local Minkowski distance measured by the falling observer.

## Data gate: keep unresolved states unfilled

The [729-level Bound 10 logarithmic registry](BOUND10_729_LOG_AREAL_RADIUS_20261027.csv) is reused **as a set of radii**, not 729 equal-time events. At each radius compute the model clock **only if**

    r_stop <= r <= 100*r_s .

This leaves **418 of the 729 logarithmic registry radii** within the chosen calculation segment and the remaining **311** with a blank proper-time readout: either outside the sampled starting radius or beyond the defined cutoff. Station 001 is the Planck reference and station 000 is the mathematical center, and both have **unknown** physical clock values. The event horizon and high-curvature cutoff are also recorded separately as exact analytic anchors, rather than claiming they align with integer-valued stations.

Finite-precision precaution: the cutoff-to-center formal time is only ~6.69e-44 seconds compared with a ~28-second horizon-to-center duration. Subtracting those two numbers in ordinary floating-point arithmetic cannot resolve the remainder. The implementation carries an independent analytic **time remaining to the cutoff** and a separate dimensionless Planck-time ratio, instead of falsely reporting a high-precision arrival time at r=0.

## Relationship to moving train and 24! registry

Earlier [Bound 09 shared Galactocentric translation](BOUND09_NATURAL_BOUND_2026-10-27.md) remains a coordinate visualization. A common uniform motion does not change a local observer's proper time or Schwarzschild spacetime invariants. Sgr A*'s actual translational motion is not measured in this record.

The [Bound 08 exact cyclic 24! permutation state](BOUND08_NATURAL_BOUND_2026-10-27.md) still provides Gray 000→001 and the last→first logical seam. **Factorial index is not the infaller's clock**; no step in the permutation ring, Galactocentric station grid, or interactive control is asserted to move physical mass.

## Output artifacts and executed tests

- [Stand-alone interactive falling-clock and proper-time viewer](bound11-proper-time.html): exterior vs interior sample-segment clock controls, curvature plot, tidal coefficients, exact separate 729 radius registry and 24! Gray ring.
- [Radial geodesic, curvature and tidal model with explicit stop](bound11_infall_proper_time_core.js).
- [729 radius positions and gated proper-time values](BOUND11_729_FALL_CLOCK_20261027.csv).
- [Exact event-marker table](BOUND11_INVARIANT_MILESTONES_20261027.csv).
- [Machine-readable evidence and test audit](BOUND11_INVARIANT_FALL_AUDIT_20261027.json).

The committed JS was retrieved and **executed**: model proper-time start/horizon/cutoff, analytic mass-independent ratio, geodesic/tidal and curvature checks passed, as did 2,002 sample points across exterior/interior progress. The self-contained HTML's four scripts passed JavaScript syntax checks and a simulated-browser DOM interaction test (start, horizon, cutoff, Planck 001 unknown, center 000 unknown, exact rank seam and input guard). The local code checks are NOT a real browser screenshot, nor proof that GitHub Pages serves the new page.

## Natural next boundary 12

Introduce a local freely falling orthonormal tetrad and an infinitesimal body separation vector, then use geodesic deviation to quantify radial stretch and transverse compression at each valid point. Test a **stated** sample-body size and chosen tolerance threshold separately from the actual observed gravitational data. Compare the nonspinning Schwarzschild result with a distinct Kerr spinning candidate before inferring any physical interior behavior. Do not claim the unmeasured center is known.

**Freeze:** new files only, previously published bounds 01–10 remain unaltered. The three witnesses are source measurement, explicit metric derivation and independent test receipt; no votes or consensus threshold.
