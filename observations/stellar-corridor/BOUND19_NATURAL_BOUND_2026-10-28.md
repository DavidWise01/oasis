# Natural Bound 19 — Pre-Cauchy convergence and mass-flux conservation gate (2026-10-28)

Evidence: `ITD_BOUND19_NEAR_INNER_RN_CONSTRAINT_FLUX_GUARD_20261028`

Freeze: `APPEND_ONLY` / `SPHERICAL_CHARGED_RN_PLUS_SCALAR` / `FIVE_CONVERGENT_NEAR_INNER_PATCHES` / `THREE_HARD_ABORTS` / `AUTOMATIC_GLOBAL_GRID_REFINEMENT_NOT_LOCAL_AMR` / `INDEPENDENT_MASS_FLUX_IDENTITIES` / `24_FACTORIAL_SEPARATE` / `NO_MASS_INFLATION_CLAIM`.

This appends to [Bound 18 coupled characteristic evolution](BOUND18_NATURAL_BOUND_2026-10-27.md). **Bounds 01–18 are unchanged.**

## Physical purpose and precise limitation

The previous bound solved the spherical Einstein–Maxwell–neutral-massless-scalar double-null equations on a small trapped-region grid near `r0=1.2` with charge `Q/M0=0.8`. Natural Bound 19 tests how far the *same equation solver* can be run, at fixed finite coordinate extent and scalar inputs, with a set of **independently prescribed starting radius values** approaching the ideal charged Reissner–Nordström (RN) inner horizon.

These starts are **different characteristic initial-value problems**, not later points along a single actual trajectory. In particular, the mass values below **must not** be interpreted as a time sequence or the Hawking mass evolving along one Cauchy horizon.

The ideal background horizons in `G=c=M0=1` units are `r+=1.6` and `r−=0.4`. The rotating Kerr horizon in Bounds 14–16 is a distinct spacetime, not a physical consequence of this RN charge example. The assumed `Q/M=.8` and scalar pulses were not measured for Sagittarius A*.

## Equations reused without modifying the frozen solver

The 1+1D double-null metric is

    ds²=−exp(2σ) du dv+r² dΩ².

Three *fully coupled* equations are evolved:

    r_uv = −r_u r_v/r − exp(2σ)/(4r)*(1−Q²/r²)
    σ_uv = r_u r_v/r² + exp(2σ)/(4r²)*(1−2Q²/r²) − φ_u φ_v
    φ_uv = −(r_u φ_v+r_v φ_u)/r.

The two independently monitored null constraint residuals remain

    C_uu = r_uu −2σ_u r_u +r(φ_u)²
    C_vv = r_vv −2σ_v r_v +r(φ_v)².

The charged Hawking mass, derived from the evolving geometry rather than assigned by hand, is

    m = (r/2)[1+4exp(−2σ)r_u r_v+Q²/r²].

### New independent mass conservation witness

From the same spherical Einstein–Maxwell–real-scalar equations, the charged mass function satisfies the following characteristic flux identities in these field normalizations:

    m_u = −2r² exp(−2σ) r_v (φ_u)²
    m_v = −2r² exp(−2σ) r_u (φ_v)².

The validator computes `m_u` and `m_v` from finite differences of the numerical mass grid **independently** of the right-side flux predictions. Both discrepancies must shrink under refinement. For trapped regions `r_u<0, r_v<0`, the predicted mass derivatives are nonnegative with these chosen null-coordinate orientations.

This additional test catches cases where the three evolution equations might numerically look smooth while the mass identity does not converge.

## Resolution escalation and declared stop

The input data retain the same null coordinate extents `0<=u,v<=0.4`, background `Q=.8`, and two smooth scalar boundary pulses with default amplitudes `A=.02` on one null arm and `B=.015` on the other.

For each candidate starting radius, the program tries uniform square-grid refinements:

    N=24 → 48 → 96 → 192.

At every level it verifies positive, finite evolved radius, a trapped midpoint and that the smallest computed radius (including the far corner) stays above a **chosen** guard,

    r_guard = r− + 0.0005(r+−r−) = 0.400600.

At the end it checks that mass, both constraint RMS values, and both independent mass-flux identity residuals converge by an approximately fourfold factor under grid halving (accepted range `2.7<ratio<5.3`).

**This is automatic global resolution escalation, not locally adaptive mesh refinement.** The 0.05%-of-horizon-gap guard is a deliberately selected numerical cutoff, not a derived geometric invariant, physical safe surface or universal natural constant. An evolution failure or guard breach produces an explicit **ABORT**, not extrapolated values.

## Executed default scan

| Assumed starting r0 | Smallest solved r, including far corner | Checkpoint mass, N=192 | Status |
| ---: | ---: | ---: | --- |
| 0.800 | 0.5824236743 | 1.0024656080 | ACCEPT |
| 0.600 | 0.4331215121 | 1.0013731001 | ACCEPT |
| 0.500 | 0.4085788110 | 1.0009453547 | ACCEPT |
| 0.450 | 0.4029621804 | 1.0007701227 | ACCEPT |
| 0.420 | **0.4007910326** | **1.0006852506** | ACCEPT |
| 0.415 | withheld | withheld | ABORT: pre-inner guard crossed |
| 0.410 | withheld | withheld | ABORT: pre-inner guard crossed |
| 0.405 | withheld | withheld | ABORT: original solver domain lost |

The last five accepted entries are **different initial characteristic spacetime configurations**. Their checkpoint mass values decreasing as `r0` decreases therefore cannot be read as the mass shrinking along one physical worldline. Conversely, positive mass changes at an individual checkpoint do **not** show divergent mass inflation near an inner horizon.

At `r0=.42`, the furthest grid corner reaches `r=0.4007910326`, still greater than the declared 0.400600 guard. The mass at `u=v=0.2` is `1.0006852506`.

### Deepest accepted convergence check, N=192

| Test | Result |
| --- | ---: |
| Checkpoint mass refinement factor | **4.000587** |
| C_uu RMS refinement factor | **3.982937** |
| C_vv RMS refinement factor | **3.983903** |
| Independent m_u identity error refinement | **3.992708** |
| Independent m_v identity error refinement | **3.992163** |
| C_uu RMS | 2.589814 × 10^-6 |
| C_vv RMS | 1.582429 × 10^-6 |

These ratios were calculated from N=96 to N=192 (and earlier N=24→48→96 stages); they reflect **second-order numerical convergence** of this finite characteristic patch. They do not establish convergence of the *limit* `r→r_-`.

### Initial-amplitude dependence — separate controlled witness

For `r0=.415`, the default amplitudes `A=.02,B=.015` breach the chosen guard and are halted. Reducing the **assumed input pulses** to `A=.015,B=.01125` allows a distinct four-grid evolution to pass, with smallest radius `0.4006319630` and checkpoint mass `1.0003753791`.

This does not mean the reduced disturbance protects a real astrophysical inner horizon. It demonstrates that the chosen model stopping condition is **initial-data-dependent**, not an intrinsic physical singular surface.

## Registry and algorithmic traceability

The new [field and mass-flux dataset](BOUND19_729_NEAR_INNER_FIELD_MASS_FLUX_WITNESS_20261028.csv) contains exactly **five accepted regions × 27×27 interior samples = 3,645 rows**. Each row reports null coordinates `u,v`, metric radius and conformal factor, scalar field, charged Hawking mass, both null derivatives, both scalar fluxes, both null constraint residuals, and both independent finite-difference mass-flux balances. **No samples from aborted regions were promoted as accepted.**

A [radius/acceptance gate table](BOUND19_PRECAUCHY_RADIUS_GATES_20261028.csv) preserves all eight default outcomes plus the reduced-amplitude `r0=.415` control. A separate [resolution and mass-conservation table](BOUND19_FOUR_REFINEMENTS_CONSTRAINT_MASS_FLUX_20261028.csv) records every completed grid level, including incomplete/aborted cases; no artificial missing values are replaced with zeros.

Standalone artifacts:

- [Numerical gate and mass-flux witness source](bound19_inner_approach_gate_core.js), depending only on the original unchanged Bound18 source.
- [Interactive radius, input amplitude and error-convergence explorer](bound19-pre-cauchy-constraint-gate.html), with both JS cores embedded and a self-check.
- [3,645 accepted samples](BOUND19_729_NEAR_INNER_FIELD_MASS_FLUX_WITNESS_20261028.csv).
- [Acceptance, guard and abort decisions](BOUND19_PRECAUCHY_RADIUS_GATES_20261028.csv).
- [Grid, null constraints and mass-flux convergence](BOUND19_FOUR_REFINEMENTS_CONSTRAINT_MASS_FLUX_20261028.csv).
- [Full input/provenance/test and limitation audit](BOUND19_AUDIT_20261028.json).

The exact 24! SJT register remains a separate logical addressing scheme. Forward `000→001` and cyclic last `100→000` do not physically move scalar pulses or change Einstein geometry.

## Literature and independent witnesses

- Burko and Ori, *Late-time evolution of nonlinear gravitational collapse*, [Phys. Rev. D 56, 7820 (1997)](https://doi.org/10.1103/PhysRevD.56.7820), uses double-null free evolution and monitors rather than enforces interior constraints; their work demonstrates second-order convergence in a different full collapse and tail study.
- Droz, *Numerical investigation of black hole interiors*, [Phys. Rev. D 55, 3575 (1997)](https://doi.org/10.1103/PhysRevD.55.3575), studies a mass-inflation-type null singularity in a physically different interior evolution.
- Ori, *Inner structure of a charged black hole: An exact mass-inflation solution*, [Phys. Rev. Lett. 67, 789 (1991)](https://doi.org/10.1103/PhysRevLett.67.789).

These sources motivate the near-inner-horizon problem. They **do not** verify the numerical results or an observed Sgr A* mass-inflation history.

All production source and CSVs were written to GitHub. The committed gate source was fetched and executed, passing five accepted regions, three stopped default regions and the reduced-input control. The HTML's four embedded scripts compiled, and a simulated DOM interaction test passed deep accepted, stop, reduced pulse recovery, evolution error, and 24! Gray seam. Actual browser rendering and live GitHub Pages deployment were not independently verified.

## Next natural Bound 20

Move from **separate near-inner initial data** to a **single globally consistent long-advanced-time characteristic problem** with controlled external late-time incoming/outgoing tail data. Add genuine local adaptive meshing or a regularized gauge when the resolution gate demands it; track both null constraints, independent mass-flux identities and gauge-invariant Hawking mass along the putative inner-horizon direction. A consistent curvature diagnostic and independent convergence toward the limit are necessary before claiming mass inflation. Stop before unresolved gradients or unknown quantum-regime physics.

**Freeze:** Bounds 01–18 are unmodified. No physical zero core, Kerr interior continuation or actual Sgr A* scalar flux is asserted.
