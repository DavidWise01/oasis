# Natural Bound 18 — Coupled Einstein–Maxwell–scalar evolution with monitored null constraints

**Evidence:** `ITD_BOUND18_SPHERICAL_EINSTEIN_MAXWELL_SCALAR_CHARACTERISTIC_EVOLUTION_20261027`

**Date:** 2026-10-27

**Freeze state:** `APPEND_ONLY` / `FULLY_COUPLED_SPHERICAL_CHARACTERISTIC_EVOLUTION` / `EXACT_VACUUM_RN_CONTROL` / `DOUBLE_NULL_CONSTRAINTS_MONITORED` / `SECOND_ORDER_NUMERICAL_CONVERGENCE_VERIFIED` / `NO_INNER_HORIZON_MASS_INFLATION_CLAIM` / `24_FACTORIAL_SEPARATE`.

This is the append-only successor to [Check 17](BOUND17_NATURAL_CHECK_2026-10-27.md). No files from Bounds 01–17 have been modified. The original 729 Galactic corridor stations and the symbolic 24! ring remain unchanged.

## Why this is a new boundary

Check 17 established the four-region **local Dray–’t Hooft–Redmount thin-shell junction**, including the nonlinear two-shell crossing term, but it did not evolve the underlying metric in time.

This Bound 18 numerically evolves a small, fully coupled **spherically symmetric Einstein–Maxwell–neutral massless scalar** region. It computes three dynamical fields, `r(u,v)`, `sigma(u,v)`, `phi(u,v)`, in double-null coordinates, allowing scalar flux to react back on metric geometry. The two null constraints are **monitored independently** throughout the interior; a vacuum exact-solution control and grid convergence check the numerical method.

**It is not the rotating Kerr model.** Charged spherical Reissner–Nordström (RN) and rotating Kerr have different matter/geometry, and their charge Q and spin chi are not interchangeable. This small simulated trapped-region patch also does **not** reach the RN inner Cauchy horizon, so the run does not claim to calculate the late-time mass-inflation singularity.

## Evolution equations, spherical metric and mass

Use `G=c=M0=1`, fixed hypothetical electric charge `Q=0.8`, and

    ds² = −exp(2sigma) du dv + r² dOmega²,  g_uv=−exp(2sigma)/2
    r_uv      = −r_u*r_v/r − exp(2sigma)/(4r)*(1−Q²/r²)
    sigma_uv  = r_u*r_v/r² + exp(2sigma)/(4r²)*(1−2Q²/r²) − phi_u*phi_v
    phi_uv    = −(r_u*phi_v+r_v*phi_u)/r.

The constraint fields, not substituted as interior evolution equations, are

    C_uu = r_uu −2sigma_u*r_u + r*(phi_u)²
    C_vv = r_vv −2sigma_v*r_v + r*(phi_v)².

Their exact Einstein–matter solution values are zero. Numerical finite-difference residuals should decrease under grid refinement.

The spherical charged Hawking mass function is calculated from evolved metric derivatives:

    m = r/2 * [1 + 4r_u*r_v/exp(2sigma) + Q²/r²].

For scalar-free exact RN, it equals the background mass `M0=1` throughout the patch. The scalar stress-tensor flux sources along the null directions are proportional to `(phi_u)^2` and `(phi_v)^2`. The neutral scalar does not alter the constant background electric charge Q.

**Scientific references:** Burko and Ori, *Late-time evolution of nonlinear gravitational collapse*, [Phys Rev D 56, 7820 (1997)](https://doi.org/10.1103/PhysRevD.56.7820); Mädler, Gannouj and Gallo, *Characteristic initial value problems for the Einstein–Maxwell–scalar field equations in spherical symmetry*, [Phys Rev D (2025)](https://doi.org/10.1103/f5fc-zpld). These establish the modeling framework, not the astrophysical accuracy of any arbitrary initial pulse in this record.

## Initial data and null boundary constraints

Set the intersecting null arms `u=0` and `v=0`, each of coordinate extent `0<=s<=L=0.4`. At their intersection use `r0=1.2`, within the exact RN trapped region for `M0=1, Q=0.8`, whose ideal horizons are `r+=1.6, r−=0.4`. The two null radius derivatives are initially negative.

Along *each* arm choose the simple RN-compatible radius gauge and a smooth scalar pulse:

    F(r) = 1 − 2/r + Q²/r²
    dr/ds = F(r)/2
    phi(s) = amplitude * sin²(pi*s/L).

Thus the pulse is zero at the shared corner and smooth on the sampled segment. The angular mass/charge and scalar values at the shared corner agree between both arms.

**Crucially, the edge metric is not kept at its vacuum value after adding matter.** Solve the corresponding null Einstein constraint along each input arm:

    sigma_RN(s) = (1/2) ln[−F(r(s))]
    sigma_s(s) = sigma_RN_s(s) + r(s)*(phi_s)^2/F(r(s)).

This follows from `r_ss−2sigma_s*r_s + r(phi_s)^2=0` and `r_s=F/2`. The code integrates `dr/ds=F/2` with RK4 and the scalar correction with per-cell Simpson integration. The corner sigma equals the vacuum value `(1/2)ln[−F(r0)]` and the two characteristic arms share it.

Four distinct initial-data experiments:

| Scenario | u-axis pulse A | v-axis pulse B |
| --- | ---: | ---: |
| Exact RN vacuum control | 0 | 0 |
| u-axis pulse only | 0.020 | 0 |
| v-axis pulse only | 0 | 0.015 |
| Both characteristic pulses | 0.020 | 0.015 |

These are hypothetical **dimensionless** fields and charge—not measured Sgr A* values. "Two streams" means two independent characteristic scalar inputs, not the two infinitesimally thin delta-function shells from Bound 17.

## Numerical solver and convergence

The production engine uses a symmetric **second-order double-null diamond rule** for all three fields:

    Y_NE = Y_SE + Y_NW − Y_SW + h² RHS(midpoint).

All field values and their two first derivatives at the cell midpoint are determined from all four cell corners; the initially unknown north-east corner is solved with eight fixed-point iterations. This is **not** a frozen-background test scalar calculation: both `r` and `sigma` change with scalar flux via the full coupled PDE right-hand sides.

Evolve a square characteristic patch `0<=u,v<=0.4` using four refinements `N=24, 48, 96, 192` grid cells per axis. Evaluate the charged mass at the fixed checkpoint `u=v=0.2`, independent of resolution.

| Input configuration | Mass at N=24 | Mass at N=96 | Mass at N=192 |
| --- | ---: | ---: | ---: |
| Vacuum RN control | 1.00000189045 | 1.00000011815 | 1.00000002954 |
| u-axis only (A=0.02) | 1.00353422336 | 1.00353240593 | 1.00353231509 |
| v-axis only (B=0.015) | 1.00197776552 | 1.00197596674 | 1.00197587682 |
| Both A=0.02, B=0.015 | 1.00564903691 | 1.00564715863 | **1.00564706476** |

The **independent mixed nonlinear response** at N=192 is

    m_both - m_u_only - m_v_only + m_vacuum
      = +0.0001389023892843788 M0.

This is nonlinear feedback under a declared finite initial-value problem; do not mistake it for the unbounded mass-inflation phenomenon at the Cauchy horizon.

**Check 1: vacuum exact solution.** As N increases, the vacuum mass approaches exactly 1. At N=192 the residual is only +2.95×10^-8.

**Check 2: solution convergence.** For the both-pulse test, successive coarse-to-fine differences shrink by ratios **4.00209** and **4.00059**, consistent with second-order convergence. Similar ~4 ratios occur in the other three scenarios.

**Check 3: both interior null constraints.** Their root-mean-square finite-difference residuals, checked across **(N−1)^2** interior grid points, are:

| N | RMS C_uu (both pulses) | RMS C_vv (both pulses) |
| ---: | ---: | ---: |
| 24 | 3.9507235e−4 | 2.2219650e−4 |
| 48 | 1.0164827e−4 | 5.7169368e−5 |
| 96 | 2.5706552e−5 | 1.4458002e−5 |
| 192 | **6.4591609e−6** | **3.6327884e−6** |

The final refinement reduces the RMS residuals by approximately 3.98 times in **both** directions, rather than holding them artificially at zero. These are dimensionless coordinate-residual norms, not measured physical uncertainties.

**Check 4: no forced interior constraint projection.** The code integrates only the three evolution PDEs inside the grid and then independently evaluates C_uu and C_vv from the numerical solution. This makes convergence a meaningful check.

## Append-only 729 and 24! separation

For each of the four scenarios, an [independent N=192 numerical grid](BOUND18_729_DOUBLE_NULL_MASS_FLUX_CONSTRAINT_SAMPLES_20261027.csv) was sampled at exactly **27×27 interior characteristic points = 729 values**. The combined file has **2,916 data records**, including:

- two null coordinates, field radius, metric `sigma`, scalar `phi`, charged Hawking mass and mass departure from background;
- independent scalar flux strengths along u and v;
- both actual finite-difference null-constraint residuals;
- trapped-region signs `r_u<0` and `r_v<0`;
- explicit status that this is numerical geometry, not stellar observation or a time series.

The [four-scenario, four-grid convergence table](BOUND18_FOUR_REFINEMENTS_CONSTRAINT_CONVERGENCE_20261027.csv) provides 16 separate checks.

The **existing** symbolic `24!` cycle still maps rank 000→001, last→000 and reverse seam; advancing that logical index **does not move the scalar flux, physical mass or proper time**. Neither the 729 output sampling grid nor the 24! address register represents a real star, a Kerr-geometry physical orbit or a finite-element body.

## Interactive and reproducible artifacts

- [Standalone live-in-browser double-null field evolution](bound18-characteristic-field-evolution.html) with A/B amplitude selectors, vacuum/one/two-pulse configuration, 48/96/192 resolution, charged mass heatmap, two separate constraint monitors and the 24! independent register.
- [Dependency-free JS characteristic Einstein–Maxwell–scalar engine](bound18_double_null_ems_core.js).
- [All four × 729 representative field samples](BOUND18_729_DOUBLE_NULL_MASS_FLUX_CONSTRAINT_SAMPLES_20261027.csv).
- [16 resolution and constraint records](BOUND18_FOUR_REFINEMENTS_CONSTRAINT_CONVERGENCE_20261027.csv).
- [Machine-readable equations, provenance, tested outputs and limitations](BOUND18_CHARACTERISTIC_AUDIT_20261027.json).

The committed JS was retrieved and **executed**. It passed all four scenario refinements, vacuum RN limit, negative trapped-region derivative checks, independent null-constraint convergence, finite cell residual guards and nonlinear two-stream checkpoint checks.

The self-contained HTML's three scripts passed syntax tests. A simulated browser DOM exercised vacuum, both streams, 96→192 refinement, changed flux input, the 24! seam, and out-of-range rank protection. Live GitHub Pages deployment and graphical rendering in a real browser were not independently verified.

## Strict boundary of this result

- The run is small in coordinates, with radius remaining near 1.2; it does **not** approach the RN Cauchy horizon `r_-=0.4`.
- No physically observed black-hole charge or scalar field initial data were used.
- Numerical convergence on this patch does **not** prove that a late-time mass-inflation singularity forms at the Cauchy horizon.
- The simulation is charged spherical RN+scalar, not rotating Kerr. Coupling its scalar mass result directly to prior Kerr spin would be unjustified.
- No observer survival, Planck-length core, quanta substructure, resolved physical singularity or stable Cauchy-horizon extension has been inferred.
- Gauge-dependent coordinate derivatives must not be confused with locally measured proper acceleration.

## Next natural bound — 19

Advance the **coupled** system toward the inner-horizon regime under an adaptive/resolved double-null gauge and with genuine long-time incoming/outgoing initial tails. Monitor charge, the spherical Hawking mass, both constraint propagation channels, geometric curvature and refinement errors; enforce a numerical STOP before underresolved gradients or invalid classical conditions. Only after independent convergence near the horizon would a mass-inflation claim be warranted. The rotating Kerr problem remains separate.

**Frozen:** earlier Bounds 01–17 remain unchanged. The original 729 corridor, logarithmic radius registry and exact 24! logical ring retain their independent provenance.
