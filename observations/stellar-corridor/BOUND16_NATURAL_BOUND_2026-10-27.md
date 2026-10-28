# Natural Bound 16 — Kerr inner-horizon blueshift and the mass-inflation limitation (2026-10-27)

Evidence ID: `ITD_BOUND16_KERR_CAUSAL_PERTURBATION_BLUESHIFT_DIAGNOSTIC_20261027`.

State: `APPEND_ONLY` / `STATIONARY_KERR_KAPPA_MINUS` / `ASSUMED_PRICE_TAIL_ENVELOPE` / `ADVANCED_NULL_TIME_NOT_PROPER_TIME` / `LOG_DOMAIN_SENSITIVITY_ONLY` / `NO_BACKREACTION_SOLVED` / `CHI_ZERO_UNDEFINED` / `24_FACTORIAL_LOGICAL_ONLY`.

This extends the frozen [Bound 15 horizon-penetrating observer model](BOUND15_NATURAL_BOUND_2026-10-27.md). All previous Bound 01–15 files, including the original 729 linear Galactic stations, the 729 logarithmic areal-radius references, and the 24! SJT register, remain unchanged.

## Natural bound: dynamical stability, not just coordinate regularity

Bound 15 proved that the **ideal stationary Kerr** coordinate/tetrad can pass continuously through the future *outer* event horizon. It did not establish the astrophysical stability of the *inner* horizon. Once outgoing and ingoing radiation/perturbations are present, repeated blueshift can magnify even weak late-time tails; nonlinear gravitational backreaction is the mass-inflation problem.

Historical research: Poisson and Israel, [Phys Rev D 41,1796 (1990)](https://doi.org/10.1103/PhysRevD.41.1796), show the radiative-tail/inner-horizon blueshift mechanism and unbounded growth in their model. More recent analysis by Carballo-Rubio, Di Filippo, Liberati and Visser, [Phys Rev Lett 133,181402 (2024)](https://doi.org/10.1103/PhysRevLett.133.181402), studies finite exponential growth in evolving inner trapping horizons, including without exact eternal Cauchy horizons. These works motivate the modeling direction but do **not** validate any particular arbitrary perturbation amplitude chosen in this file.

## Actual established stationary Kerr quantity

Use the same mass as previous bounds (GRAVITY collaboration Sgr A* dynamical mass, 4.297 million solar masses) and independent assumed spin values `chi=0,.5,.9,.99`. Let

    r_g = GM/c² ; t_g = r_g/c
    q = sqrt(1−chi²)
    r_± = r_g (1±q)
    a = chi * r_g

For `0<chi<1`, the *absolute value* of the ideal Kerr inner horizon surface gravity is

    |kappa_-| [1/m] = (r_+−r_-)/(2(r_-²+a²))
    beta = r_g |kappa_-| = q/[2(1−q)]
    gamma_- [1/s] = c |kappa_-| = beta/t_g
    e-fold time [s] = 1/gamma_-.

The Killing-horizon generator is normalized in the standard asymptotically flat stationary Kerr convention. This expression is a geometrical property of the **unperturbed** metric, *not* a directly observed inner-horizon blueshift. The inner `kappa_-` is negative in the conventional signed form; `gamma_-` is its positive magnitude.

Citation for the signed Kerr inner/outer horizon quantity: Pradhan, [Eur Phys J C 74, 2887 (2014)](https://doi.org/10.1140/epjc/s10052-014-2887-2).

### Measured vs model assumptions

- The **mass** is tied to the Sgr A* stellar-orbit analysis, not to internal observations.
- **Spin values** are parameter scenarios, not a fit of Sgr A* spin.
- The **power-law incoming tail**, amplitude and reference advanced-time origin are invented modeling inputs for sensitivity analysis, not measured disturbances.
- No evolving metric, stress-energy tensor, null geodesic perturbation, physical mass parameter, or curvature-inflation history has been solved here.

**Critical domain exclusion:** `chi=0` has only the Schwarzschild outer event horizon; the formal algebraic `r_-=0` coincides with the central singularity and is **not** an inner Kerr Cauchy horizon. Do **not** evaluate the divergent rotating inner-horizon rate at `chi=0`. The source code returns `null` and the 729-row chi=0 witness leaves its proxy columns blank.

## Explicit toy perturbation: exponentially amplified power-law tail

Define an advanced Kerr null coordinate `v` with **dimensions of length** in the convention `v=ct+...`. Fix a positive late reference `v_0` and define

    x = (v−v_0)/r_g >= 0
    x_0 = v_0/r_g > 0
    Delta v/c = x t_g,  a referenced coordinate-time interval (not infaller proper time).

An *illustrative, dimensionless* competing-decay/growth model is

    S(x) = epsilon * (1+x/x_0)^(-p) * exp(beta*x).

Here `epsilon>0` is an assumed small initial perturbation amplitude; `p>0` is an assumed late-time tail exponent, and `x_0>0` is a chosen advanced-time origin. These are **scenario choices** and are not known Sgr A* fluxes.

For numerical stability, evaluate **only the logarithm**:

    log10 S = log10 epsilon + [beta*x - p ln(1+x/x_0)]/ln(10)
    d ln S/dx = beta - p/(x_0+x).

The sign of the derivative identifies where the toy envelope starts increasing after any initial decrease. A user-selectable crossing `log10 S = 0` (i.e. `S=1`) is only a convenient **arbitrary computational threshold**, *not* the onset of physical mass inflation, an event on the observer's proper clock, or a universal invariant-zero boundary. There is no mapping here from `S` to the Misner–Sharp mass, local energy flux, Kretschmann scalar, material stress, or actual Einstein-equation source.

### Numerical results with one explicitly stated scenario

Choose `epsilon=10^-9, p=7, x_0=100`. With the fixed Sgr A* mass in the previous bounds:

| Assumed spin | gamma_- [1/s] | Stationary e-fold [s] | Toy S=1 crossed after advanced-time shift [s] |
| ---: | ---: | ---: | ---: |
| 0.00 | undefined | undefined | undefined |
| 0.50 | 0.15270853 | 6.54842 | 138.61257 |
| 0.90 | 0.01825442 | 54.78125 | 1,321.25049 |
| 0.99 | 0.00387992 | 257.73740 | 8,198.70255 |

**These are different, unrelated clocks from the infaller's proper-time durations in Bound 15.** The latter are `28.19, 21.50, 9.48, 2.97 seconds` from an *individual outer-horizon crossing to a guard*, for spins `0,.5,.9,.99`. The new values correspond to a late advanced coordinate-time displacement measured relative to an arbitrary `v_0`, **not** to a single falling observer's travel time. Do not compare the two numbers as physical onset versus survival without constructing a causal, coupled model.

A change in `epsilon`, `p` or `x_0` changes the arbitrary toy threshold location. The Kerr geometry itself is not changed by toggling those controls, so any inference of actual `r_-` displacement, quantum transition, or physical central core from those toggles is invalid.

## Reproducible artifacts

- [Self-contained interactive perturbation/blueshift viewer](bound16-mass-inflation-sensitivity.html). Select spin, log initial amplitude, tail exponent, advanced-time reference, late-time displacement; inspect logarithmic tail and blueshift components, independent Bound15 proper-time anchor, and full 24! Gray cycle.
- [Pure JS Kerr inner surface gravity and log perturbation engine](bound16_mass_inflation_diagnostic_core.js).
- [Four × 729 advanced-time witness rows](BOUND16_729_ADVANCED_TIME_PERTURBATION_SPIN_SWEEP_20261027.csv). No claim of observed gamma-ray, optical or gravitational wave events. All undefined chi0 inner-horizon values are blank.
- [Separate four-row spin and toy threshold table](BOUND16_INNER_SURFACE_GRAVITY_TOY_THRESHOLD_20261027.csv).
- [Machine-readable provenance and test receipt](BOUND16_MASS_INFLATION_AUDIT_20261027.json).

## Executed tests and traceable limits

The actual committed source was retrieved from GitHub and executed. The engine checks:

1. Signed vs absolute inner Kerr surface-gravity identity, dimensions and e-folding reciprocal.
2. Nonrotating chi0 domain rejection and null propagation.
3. Analytic log-proxy derivative against a finite-difference calculation, all rotating spins at five advanced-time positions.
4. Location of the minimum of the exponential-vs-power-law toy envelope, plus precise threshold-upcrossing bisection.
5. Stable log-domain calculations at advanced times too large for direct exponentials.
6. Input guards for invalid epsilon or domain.
7. The dependent **Bound15 infaller proper clock remains unaltered**, and its check is executed by the page.
8. The HTML has five compiled inline JavaScript scripts; a simulated DOM/control test covered spin selection, epsilon/p/x0 adjustments, reference/threshold/latest events, chi0 null, factorial 000→001 and final→first/reverse Gray seam, and invalid BigInt rank input.

**Not independently checked:** actual GUI graphics in a real browser, deployment of a live GitHub Pages URL, numeric solution of perturbed Einstein equations, true late-time Price-law tail normalization for Sagittarius A*, exact coupled ingoing/outgoing flux or realistic material survival.

## Three witnesses, no quorum

- **Theory:** published radiative-tail blueshift and Cauchy-horizon instability.
- **Geometry:** signed Kerr inner horizon surface gravity and dimensional conversion.
- **Implementation:** tested logarithmic tail/growth sensitivity with no exponent overflow and no physics mislabeled as direct observation.

The `24!` registry is unchanged. The 729 samples are **a purely numerical advanced-time grid**, not 729 observed stars, Planck pixels or physical self-replicating core elements.

## Next natural Bound 17 — Coupled two-stream field equations

A physically stronger follow-up would specify incoming and outgoing energy fluxes, initial data on two null hypersurfaces, and an Einstein–matter system (or a rigorously derived perturbative reduction). Numerically solve mass/curvature feedback, check the constraints and resolution convergence, and stop when the classical approximation ceases to be credible. Do not simply relabel the scalar `S` as physical mass inflation.

**Freeze:** Bound 16 adds new artifacts only, leaves Bound 01–15 and the full `24!` toroidal address traversal intact, and does not assert that a stable inner horizon or a discoverable Planck-sized central surface exists.
