# Natural Bound 15 — Ingoing Kerr: a finite local tetrad across the future outer horizon (2026-10-27)

Evidence: `ITD_BOUND15_FUTURE_INGOING_KERR_OUTER_HORIZON_20261027`

Freeze state: `BOUND15_VERIFIED` / `E1_LZ0_Q0` / `INGOING_KERR_CHART` / `PARALLEL_TETRAD_CONTINUOUS_AT_OUTER_HORIZON` / `16_FULL_RIEMANN_TESTS` / `PRE_CAUCHY_GUARD` / `24_FACTORIAL_RANK_NOT_CLOCK`.

**Append only.** Earlier Bounds 01–14 and their 729 linear/logarithmic station datasets, independent Gaia evidence, and 24! SJT/Gray ring were not modified.

## Main observation versus calculation

The earlier Bound 14 Boyer–Lindquist (BL) description becomes coordinate-singular as r approaches the Kerr outer event horizon. This is not itself a curvature singularity. Change from BL coordinates (t,r,theta,phi) to advanced future-ingoing Kerr coordinates (v,r,theta,phiPlus):

    dv      = dt + (r²+a²)/Delta dr
    dphiPlus= dphi + a/Delta dr
    Delta   = r²-2Mr+a²          [G=c=1 geometric units]

The resulting metric has **no inverse Delta** and is regular on the future horizon. In dimensionless variables `y=r/rg`, `rg=GM/c²`, `chi=a/rg`, `Sigma=y²+chi² cos²theta`:

    g_vv       = -1+2y/Sigma
    g_vr       = +1
    g_vphiPlus = -2chi y sin²theta /Sigma
    g_rphiPlus = -chi sin²theta
    g_thetatheta = Sigma
    g_phiPlusphiPlus = [y²+chi²+2chi² y sin²theta/Sigma] sin²theta

This is an exact stationary Kerr solution, not a fitted model of a real accreting interior.

**Literature:** [MNRAS 445, 2500 (2014), Appendix C](https://academic.oup.com/mnras/article/445/3/2500/1035561); [Kerr chart transformation](https://blackhole.org/reference/spacetimes-coordinates/kerr-charts/).

## Same observer, unmodified starting event and clock

Maintain exactly the same selected freely falling test-particle trajectory from Bound 14:

    E=1 (rest at infinity) ; Lz=0 ; Q=0
    theta=pi/2
    start y=200 = 100 Schwarzschild r_s
    black-hole mass = 4.297 million solar masses (GRAVITY Collaboration 2022)
    chi scenarios = 0, 0.5, 0.9, 0.99

The coordinate components of the four-velocity and basis vectors are algebraically transformed/rationalized to eliminate the 0/0 limit at `Delta=0`. Define

    P=y²+chi² ; W=sqrt(2 y P) ; S=sqrt(P) ; D=P+W

In the ingoing basis (v/rg, y, theta, phiPlus), the **parallel-transported orthonormal tetrad** is

    e0 = [(P²/D-chi²)/y²,  -W/y²,               0, -2chi/[y(2y+W)]]
    e1 = [P S/(yD),        S/y,                 0, chi S/(yD)]
    e2 = [0,               0,                   1/y, 0]
    e3 = [2chi S/[y(2y+W)],chi W/[y² S],       0, S(y²+W)/[y²D]]

All components remain finite for positive `y`, including at `y_+=1+sqrt(1-chi²)` and immediately below it. This is a **local orthonormal parallel frame** for this special `E=1,Lz=0,Q=0` geodesic, not for arbitrary Kerr trajectories.

The physical tidal eigenvalues measured in that frame remain the earlier Bound 14 values:

    lambda1 = + (2+3chi²/y²) GM/r³
    lambda2 = - (1+3chi²/y²) GM/r³
    lambda3 = - GM/r³
    lambda1+lambda2+lambda3 = 0.

The time `tau` is the **observer's proper time**. Integrate the same geodesic over the interior interval:

    dtau = (rg/c)*y^(3/2) / sqrt[2(y²+chi²)] |dy|.

This has no divergent clock at the outer horizon. Short interior intervals are integrated separately from the ~7.83-hour exterior clock to avoid catastrophic cancellation. The symbolic 24! rank remains independent of this clock.

## The next natural stop: a Cauchy-horizon guard, not invariant zero

The ideal subextremal Kerr metric has two BL horizon coordinate surfaces

    y+ = 1 + sqrt(1-chi²)   outer future event horizon
    y- = 1 - sqrt(1-chi²)   classical inner Cauchy horizon, for chi>0.

The **chosen model stop** is **one percent of the coordinate gap above the inner horizon**:

    y_stop = y- + 0.01(y+-y-)   (chi>0).

The one-percent choice is a **numerical/interpretation guard**, not a measured stability radius or a new universal physical boundary. In the nonrotating chi=0 limit, y-=0 is not a separate Cauchy horizon, so the stop y=0.02 is simply a positive-radius numerical guard before the Schwarzschild mathematical singularity.

| Hypothetical spin chi | Outer horizon y+ | Inner formal horizon y- | Chosen guard y_stop | Outer horizon → guard, proper seconds |
| ---: | ---: | ---: | ---: | ---: |
| 0.00 | 2.000000 | 0 (no separate Cauchy horizon) | 0.020000 | 28.191560 |
| 0.50 | 1.866025 | 0.133975 | 0.151295 | 21.498427 |
| 0.90 | 1.435890 | 0.564110 | 0.572828 | 9.483593 |
| 0.99 | 1.141067 | 0.858933 | 0.861754 | 2.969940 |

These durations refer solely to the **stationary, unperturbed Kerr geometry** and selected worldlines. They are not direct observations and are not predictions of a healthy observer's actual travel inside Sagittarius A*.

**Why stop?** Realistic infalling radiation and perturbations can undergo extreme blueshift/mass inflation near a Kerr inner Cauchy horizon. The ideal metric is not a robust model for that region: [Poisson & Israel (1989)](https://doi.org/10.1103/PhysRevLett.63.1663), [Poisson & Israel (1990)](https://doi.org/10.1103/PhysRevD.41.1796), and [McMaken & Hamilton (2021)](https://doi.org/10.1103/PhysRevD.103.084014). We make no physical claims beyond the selected guard, about the ring singularity, the classical Kerr extension or the Planck regime.

## Reproducible metric/connection/tidal tests

A second, mathematically independent JavaScript validator reads **the ingoing Kerr metric itself**, then:

1. Forms its inverse without using the singular BL chart.
2. Numerically differentiates the metric in y and theta to construct all Christoffel components.
3. Differentiates the connection to construct the full Riemann tensor.
4. Projects curvature onto the local observer frame, independently comparing the three tidal eigenvalues and all off-diagonal components.
5. Directly evaluates the covariant parallel-transport equation `u^nu nabla_nu e_i^mu = 0` for the three spatial axes.

**Sixteen independent tests**: spins `0, .5, .9, .99`, with points *outside*, *exactly on*, and at two points *inside* the future outer horizon, before the chosen interpretation stop.

Results after GitHub readback and actual JS execution:

- All tests **PASS**.
- Maximum normalized diagonal tidal discrepancy `8.75×10^-7`.
- Maximum normalized off-diagonal discrepancy `2.28×10^-6`.
- Maximum coordinate-component parallel-transport residual `1.18×10^-7`.
- Additional ingoing metric inverse and tetrad orthonormality: **256 comparisons PASS**, maximum orthonormality residual `1.78×10^-14`.
- The full proper-time inversion and outer-horizon clock matches the earlier Bound 14 results.
- Numerical residuals are **finite-difference errors**, not physical uncertainties or observations of Sgr A*.

No divergence is introduced merely by crossing `r_+` with this observer and coordinate chart. That does **not** prove a stable astrophysical interior.

## 729-state and 24! accounting

- [2,916 separate interior proper-time samples](BOUND15_INGOING_KERR_729_INTERIOR_SPIN_CLOCK_20261027.csv): four assumed spins × 729 equally spaced **proper-time fractions**, each starting exactly at its outer horizon and ending at the declared stopping event. Coordinates `(v/rg,y,theta,phiPlus)`, three tidal eigenvalues and their source status are recorded at each modeled sample.
- [Four independent outer/inner horizon and selected guard anchors](BOUND15_OUTER_INNER_GUARD_ANCHORS_20261027.csv).
- [Standalone interactive visual page](bound15-ingoing-kerr-horizon.html): controls for four spins, clock progress, outer horizon, midpoint and guard, three tidal axes, full four-vector local tetrad, independent test receipt and cyclic `24!` Gray register.
- [Horizon-regular core](bound15_ingoing_kerr_core.js).
- [Independent numerical curvature and parallel-transport validator](bound15_ingoing_independent_validator.js).
- [Full machine-readable audit](BOUND15_INGOING_KERR_AUDIT_20261027.json).

**Do not reinterpret station numbers as stars.** Each new 729-length series is a proper-time discretization **for one assumed spin**, not the pre-existing 729 original linear Galactic corridor stars or the 729 logarithmic radial labels. No original station observations were rewritten.

The `24!` reversible symbolic Gray cycle remains `rank=0 -> 000 -> 001`, and final rank `...999 -> Gray 100 -> 000`. Neither state transition physically moves matter across the horizon, returns an infaller from near the guard to the Sun, nor changes time.

## Three independent witnesses (no quorum)

- **Geometry witness:** advanced Kerr metric is regular across the outer horizon; exact frame computed algebraically.
- **Numerical witness:** independent metric→Christoffel→Riemann projection and covariant tetrad derivative pass across the horizon.
- **Observation/limitation witness:** source Sgr A* mass is observational, while spin values, geodesics and interior stops are assumed/modelled. Cauchy-horizon instability is established in the literature but not numerically simulated here.

The HTML embeds all needed JS and makes no third-party network requests. The five viewer scripts passed JavaScript compilation; a mock browser exercised horizon, interior midpoint, guard, changed spin, `24!` seam and invalid-rank handling. Actual Chromium screenshots and live GitHub Pages deployment are **not** verified.

## Next natural Bound 16

Test the **stability** of the ideal Kerr interior by introducing an explicitly parameterized incoming/outgoing perturbation model. Its blueshift/mass-inflation diagnostics must be labeled a new perturbative approximation; do **not** treat unperturbed Kerr metric regularity as proof that the perturbed Cauchy horizon or deeper center is physically traversable. Preserve measured versus assumed mass, initial conditions and missing quantum gravity values. The center remains unresolved.

**Freeze:** Bound 15 is append-only; Bounds 01–14 and the original 24! toroidal traversal are intact.
