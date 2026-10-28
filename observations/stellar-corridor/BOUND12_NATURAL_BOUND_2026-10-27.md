# Natural Bound 12 — Free-fall local tidal frame, Jacobi separation and finite-cloud validity (2026-10-27)

Record: ITD_BOUND12_SCHWARZSCHILD_LOCAL_JACOBI_20261027

State: `ANALYTIC_TIDAL_EIGENVALUES` / `RADIAL_AND_TWO_TRANSVERSE_JACOBI_SOLUTIONS` / `729_SEPARATE_LOG_RADII` / `FINITE_SEPARATION_VALIDITY_GATE` / `24FACTORIAL_INDEX_SEPARATE` / `EARLIER_BOUNDS_FROZEN`.

**Append only.** This is the next layer after [Bound 11: infaller proper time](BOUND11_NATURAL_BOUND_2026-10-27.md), not a modification to its historical code or physical observations.

## Physical question

How does an initially spherical arrangement of independent nearby *freely falling test particles* change shape when the reference observer falls radially into the nonspinning Schwarzschild approximation of Sgr A*?

In the parallel-transported orthonormal frame of a radial reference geodesic, the first-order geodesic deviation equations are:

    d²ξ_radial/dτ² = +[c² r_s / r³] ξ_radial
    d²ξ_transverse/dτ² = -[c² r_s / (2r³)] ξ_transverse
    d²ξ_second_transverse/dτ² = -[c² r_s / (2r³)] ξ_second_transverse

There are **two** equal transverse compressing directions and **one** radial stretching direction. The tidal eigenvalue trace is zero in Schwarzschild vacuum at each event. Trace zero does *not* mean that the volume of a finite group of particles is conserved throughout the fall.

The reference observer has **zero proper four-acceleration**. Differences in neighboring geodesics are curvature effects.

### Independent source witnesses

- "Tidal forces in Kiselev black hole" (2017), tetrad basis and geodesic deviation, https://doi.org/10.1140/epjc/s10052-017-4935-1.
- "Tidal forces in dirty black hole spacetimes" (2022), Schwarzschild tidal background and orthonormal tetrad, https://doi.org/10.1140/epjc/s10052-022-10410-0.
- CERN-hosted gravitational physics review, arXiv 2202.04658, local radial stretching and transverse compression, https://cds.cern.ch/record/2812678/files/2202.04658.pdf.
- GRAVITY Collaboration (2022), adopted Sgr A* mass 4.297 million solar masses, https://doi.org/10.1051/0004-6361/202142465.
- NIST CODATA 2022 Planck scale, https://physics.nist.gov/cuu/pdf/all.pdf.

These references validate the **equations**, not a physical observation of test-particle clouds inside Sagittarius A*.

## Exact analytical solution, no arbitrary deformation law

Use the same Bound 11 E=1 radial geodesic, corresponding to **rest at infinity**, but record the sample starting event at r_start = 100 r_s. The test particles begin with 1-meter **separations in each local orthonormal direction**, and zero initial *relative* velocity at the selected starting event. The reference observer is already moving inward at that radius.

Let u(r) = (2 r_s / 3c) (r/r_s)^(3/2), the *formal classical* proper time remaining toward r=0, and w=u(r)/u(r_start)=(r/r_start)^(3/2). With those initial conditions, direct solutions are:

    f_radial(w) = (4/5) w^(-1/3) + (1/5) w^(4/3)
    f_trans(w)  = 2 w^(1/3) - w^(2/3)
    ξ_radial    = 1 meter * f_radial
    ξ_trans_1   = 1 meter * f_trans
    ξ_trans_2   = 1 meter * f_trans
    relative_volume_factor = f_radial * f_trans²

Initial conditions at w=1 are f_radial=f_trans=1 and dξ/dτ=0. Substitution into the proper-time ODE produces coefficients +4/(9u²) radial and -2/(9u²) transverse, equivalent to the Schwarzschild equations given above. Numerical finite differences of the analytic solution were executed at three radii in both directions.

### Representative model values

| Event | Radial separation | Each transverse separation | Meaning |
| --- | ---: | ---: | --- |
| Start, 100 r_s | 1.00000 m | 1.00000 m | chosen initial condition |
| Horizon, r_s | 8.00002 m | 0.19000 m | well within 1%-smallness gate |
| 0.03 r_s | 46.18802 m | 0.03434 m | formal Schwarzschild interior, still within gate |
| 1-meter gate, r≈3,186.235 km | 504.8750 m | 0.00316659 m | local 1% threshold reached |
| Bound 11 high-curvature cutoff, r≈2.2561e-20 m | **unreportable** | **unreportable** | finite-cloud Jacobi approximation failed much earlier |

The tidal horizon eigenvalues are finite: λ_radial≈5.580977e-4 s^-2 and each λ_transverse≈-2.790489e-4 s^-2. Thus the horizon does not represent a locally singular tidal surface.

## The NEW natural bound: finite separation, not just curvature

The Jacobi equation describes **infinitesimally separated** neighboring geodesics; extrapolating a modeled finite cloud too deep can invalidate the linearization even if the background Schwarzschild curvature is still mathematically finite.

For a transparent, **chosen** 1% criterion, define the radial local curvature length:

    ℓ_curv(r) = c/sqrt(λ_radial) = sqrt(r³/r_s).

Require

    max(|ξ_radial|,|ξ_transverse|) <= 0.01 * min(r,ℓ_curv).

The 1% threshold is **not** a material failure or tearing threshold, nor a measured universal constant. It is a stringent, reproducible applicability choice. Both transverse axes receive the same comparison.

- **1m initial separation:** first smallness bound at areal r≈3,186,234.841 m (3,186.235 km). At that event radial separation≈504.875 m, transverse≈0.00316659 m, curvature length≈50,487.50 m. The remaining **formal classical** proper time to r=0 would be 1.122721198e-4 s (~0.1123 ms), but we do not extrapolate an actual finite cloud to the center.
- **1mm initial separation:** first smallness bound at r≈100,757.593 m (~100.758 km), with radial separation≈2.83912 m and transverse≈5.635e-7 m. Remaining formal time≈6.314e-7 s.
- **1µm initial separation:** another separate scenario; validity gate is smaller again. The boundary depends on initial probe size and therefore does **not** locate a universal physical black-hole surface.

All three finite-probe criteria fail before the Bound 11 named high-curvature condition `K ℓ_P^4=1`.

### 729-region bookkeeping (for the canonical 1m initial separation)

The previous Bound 10 logarithmic areal-radius grid remains *unchanged*. New [729-station results](BOUND12_729_LOCAL_TIDAL_GATED_20261027.csv) are mapped onto it, without overwriting the earlier gravitational acceleration or proper-clock files.

| Regime | Station count |
| --- | ---: |
| Within declared finite-cloud 1% smallness criterion | **74** |
| Analytic solution exists, but Jacobi finite-cloud smallness fails | **344** |
| After Bound 11 formal classical curvature stop | **200** |
| Before the selected 100 r_s reference start | **110** |
| Mathematical r=0 sentinel | **1** |
| Total | **729** |

Raw analytic factors may be stored for the 344 invalid finite-cloud entries as **mathematical diagnostics**, but the dedicated reportable 1-meter separation columns remain BLANK. The Planck-length marker and mathematical zero center also have no reportable Jacobi worldline state.

This is a different boundary from the one obtained by inventing a material tensile-strength limit. We have **not** modeled bones, spacecraft, springs or any material stress response.

## Links and executed tests

- [Standalone interactive local-frame viewer](bound12-local-tidal-frame.html). Choose 1 m, 1 mm or 1 µm initial separations, navigate exact start/horizon/applicability/cutoff markers, compare radial versus transverse factors and inspect the 729 log-radius stations.
- [Jacobi analytical engine with checks](bound12_geodesic_deviation_core.js).
- [729-station CSV, diagnostics kept separate from valid modeled values](BOUND12_729_LOCAL_TIDAL_GATED_20261027.csv).
- [Nine exact physical and bookkeeping markers](BOUND12_GEODESIC_SEPARATION_MILESTONES_20261027.csv).
- [Machine-readable independent source and interpretation audit](BOUND12_TIDAL_AUDIT_20261027.json).

The stored JavaScript source was re-read from GitHub and executed. Its tests passed: initial conditions, horizon separation factors, two eigenvalues plus zero trace, three-radius × two-axis finite-difference ODE checks, 1m/1mm bisection gates, 1,000 monotonic trajectory samples, the separate high-curvature stop and center blanking. The standalone HTML scripts are syntax checked; the visual browser deployment is not yet independently established.

## 24! and Galactic train remain unaffected

The cyclic SJT 24! registry, 000→001 Gray step, 729 address modulo and last-to-first logical seam remain independent of proper time and geodesic deviation. Their *logical* toroidal traversal does not alter physical tidal eigenvalues. The common outward Galactic train translation from Bound 09 is a frame-coordinate choice, not a source of intrinsic curvature.

## Next natural Bound 13

Choose an explicit physical body's elastic parameters and finite dimensions, then compare material stress to **local** tidal loading only within an adequate small-body approximation. In parallel, add a separate rotating **Kerr** candidate with spin explicitly parameterized; compare local tidal eigenvalues in matched freely falling tetrads. Neither material failure nor spin should be invented from the published nonspinning model. The center remains unresolved.

**Freeze:** This is Bound 12 and does not change Bounds 01–11, their observed tracer residuals, or the orbital/24! logical engine.
