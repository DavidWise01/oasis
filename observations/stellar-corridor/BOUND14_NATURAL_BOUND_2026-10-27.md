# Natural Bound 14 — An actual Kerr infaller's parallel-transported local tidal frame (2026-10-27)

Evidence ID: `ITD_BOUND14_KERR_PP_TETRAD_E1_L0_Q0_20261027`

State: `KERR_EQUATORIAL_GEODESIC` / `E1_LZ0_Q0` / `EXPLICIT_ORTHONORMAL_PARALLEL_TRANSPORTED_TETRAD` / `LOCAL_3_TIDAL_EIGENVALUES` / `INDEPENDENT_FULL_RIEMANN_VERIFIED` / `EXTERIOR_ONLY` / `729_PROPER_CLOCK_SAMPLES_PER_SPIN` / `24_FACTORIAL_RANK_NOT_TIME`.

This is an **append-only** successor to [Natural Bound 13](BOUND13_NATURAL_BOUND_2026-10-27.md). Bounds 01–13, both versions of the 729-star/model radius registry, and the 24! cyclic combinatorial operator are unchanged.

## What this bound resolves

Bound 13 could compare the stationary Kerr outer horizon, ergosurface and circular-orbit radii but could **not** legitimately reuse the Schwarzschild freefall tidal tensor as if it were a Kerr material stress. Bound 14 now fixes one actual **test-particle worldline**, constructs its explicit local freefall orthonormal tetrad, and obtains the **observer-measured electric tidal eigenvalues**. A fully numerical independent curvature calculation checks them.

This is a calculation in published **classical general relativity**, not an actual tracked person or probe inside Sgr A*.

### Initial conditions

Choose four distinct *assumed* spin scenarios `chi=0, 0.5, 0.9, 0.99`; no spin parameter is claimed to be measured for Sgr A*. Match each geodesic using

    E = 1             conserved specific energy (rest at infinity)
    Lz = 0            zero axial Killing angular momentum
    Q = 0             zero Carter equatorial-plane constant
    K = (Lz-a E)^2+Q = a^2
    theta = pi/2      equatorial geodesic throughout
    r_start = 100 r_s(Schwarzschild) = 200 r_g

Here `r_g=GM/c²`, `r_s=2r_g`, `a=chi r_g`. The word *radial* means inward-changing Boyer–Lindquist (BL) `r`; it **does not** mean fixed coordinate azimuth in rotating Kerr. Because of frame dragging, `dphi/dtau` is nonzero even though `Lz=0`.

**Inward worldline and proper time:**

    y = r/r_g;   delta = y²-2y+chi²;   P=y²+chi²
    dr/dtau = -c sqrt[2(y²+chi²)] / y^(3/2)
    dphi/dtau = (c/r_g) [2chi/(y delta)]       (BL chart only)
    y_+ = 1 + sqrt(1-chi²)
    T_chi(y) = (r_g/c) INTEGRAL(y..200) [y'^(3/2) / sqrt(2(y'^2+chi²))] dy'

The integral is evaluated with composite Simpson quadrature (1,280 intervals). The inverse mapping from proper-time fraction to BL radial `y` uses a Schwarzschild analytic starting guess and Newton updates. It is not linked to the 24! index.

The exterior calculation ends at the actual Kerr **outer** horizon `r_+=r_g(1+sqrt(1-chi²))`; **no interior trajectory is claimed**. The proper-time horizon event is finite. The BL `dt/dtau` and `dphi/dtau` components are coordinate-singular at that horizon, so the page intentionally does not display a BL tetrad there. Tidal eigenvalues are shown as **the finite exterior limit**.

## Explicit local observer and tetrad

Use the Kerr Carter **orthonormal coframe** on the equatorial exterior (signature `-+++`) and express the local four-vectors by Carter-frame components. Define

    A = P/[y sqrt(delta)]
    B = -sqrt(2 y P)/[y sqrt(delta)]
    D = -chi/y
    H = sqrt(P)/y

Then

    e_0 = (A,        B,     0, D)
    e_1 = (B/H,      A/H,   0, 0)
    e_2 = (0,        0,     1, 0)
    e_3 = (A D/H,    B D/H, 0, H)

The first vector `e_0` is the observer's timelike four-velocity. `e_1,e_2,e_3` form the local orthonormal spatial triad. All satisfy `g(e_A,e_B)=eta_AB` in the declared exterior chart.

**Special simplification:** the general Marck parallel-transport rotation for equatorial Kerr geodesics has

    dPsi/dtau = sqrt(K)/(r²+K) * [E + a/(Lz-aE)].

For this *exact* set of constants `E=1,Lz=0,K=a²`, the bracket vanishes and `dPsi/dtau=0`; the zero-spin case is the continuous limit. Therefore the displayed Carter-frame triad is parallel transported without an additional time-dependent in-plane rotation. **This special result must not be applied to arbitrary Kerr orbits or arbitrary `E,Lz,Q`.**

The four-vectors were transformed into BL coordinate components for an independent numerical covariant-derivative check, not just declared parallel by construction.

## The local 3-axis tidal field

Project the Kerr Riemann curvature into the falling tetrad. In physical SI inverse-square-seconds,

    k(r) = GM/r³ = c²/(r_g² y³)
    q(r) = chi² / y² = (a/r)²

    lambda_stretch = (2+3q) k
    lambda_polar   = -(1+3q) k
    lambda_azimuth = -k

    lambda_stretch + lambda_polar + lambda_azimuth = 0

These are **relative acceleration per unit local separation**, not the observer's own proper acceleration (zero for a geodesic) or an inferred physical solid-body stress.

At equal model **Boyer–Lindquist coordinate radius** `y`, the stretch relative to the nonrotating E=1,L=0,Q=0 reference is

    lambda_stretch(chi)/lambda_stretch(0) = 1 + (3/2) chi²/y².

For example, at `r=2r_g`, chi=0.9 gives `+30.375%` larger radial stretching than chi=0. The equation is valid at that common **equatorial BL coordinate radius** in the exterior for these two cases, *not* a comparison at the same intrinsic Kerr areal radius or two different horizon events. Because this is a coordinate-labeled comparison, do not claim a universal spin enhancement independent of how observation events are identified.

### Proper-time and horizon findings

All values computed from adopted Sgr A* mass `4.297×10⁶ M_sun` and common `r_start=200r_g`:

| Assumed chi | Kerr outer horizon y=r+/rg | Elapsed falling-clock time from 200rg |
| ---: | ---: | ---: |
| 0.00 | 2.00000 | 28,191.55969 s |
| 0.50 | 1.86603 | 28,191.90139 s |
| 0.90 | 1.43589 | 28,193.86154 s |
| 0.99 | 1.14107 | 28,196.09809 s |

The chi=0 result agrees with Bound 11's analytic Schwarzschild value `28,191.55969s` within the quadrature error (~3 microseconds). The time difference is small compared to the ~7.83-hour full segment because the initial radius is far outside the horizon; it is **not** a measurement of black-hole spin.

## Separate finite-difference GR verification

A dedicated standalone [independent connection and curvature validator](bound14_independent_curvature_validator.js) was created. It does NOT use the analytic Kerr tidal formula to calculate its projected curvature.

1. Compute the BL Kerr metric `g_mu,nu(r,theta)` at equatorial exterior sample points.
2. Independently form the metric inverse and numerical partial derivatives with respect to `r` and `theta`.
3. Construct the full `Gamma^a_bc` Christoffel symbols and `R^a_bcd` Riemann tensor.
4. Project the numeric tensor to the declared `e_0,e_1,e_2,e_3` tetrad, checking the three tidal eigenvalues and off-diagonal components.
5. Evaluate the actual parallel-transport residual `u^nu nabla_nu e_i^mu`, to check the local basis is not simply an arbitrary orthonormal rotating frame.

The test used **nine independent exterior cases**: chi = 0, 0.5, 0.9 and radius = 5, 10, 30 r_g. All passed. Max absolute residual of a *diagonal* tidal eigenvalue, divided by the natural local scale `GM/r³`, was approximately `3.7338×10^-5`; max normalized off-diagonal element approximately `3.53×10^-7`; max parallel-transport component residual about `2.61×10^-11`. These are numerical finite-difference tolerances, **not observational uncertainty or source spin uncertainty**.

The pure Kerr core also passed 384 metric orthonormality checks with maximal absolute error `2.44×10^-15`, χ=0 Schwarzschild proper-time and tidal limits, inverse proper-time consistency, radial derivative and outer-horizon frame availability guards.

## 729 × 4 registry preservation

Two **separate** append-only CSV types prevent logical-address/physical-clock confusion:

- [Four 729-sample genuine proper-time **model** series](BOUND14_KERR_729_PROPER_CLOCK_SPIN_SWEEP_20261027.csv), 2,916 rows. For each assumed spin `chi`, divide *that geodesic's proper time to its own outer horizon* into 728 equal numerical intervals. These are model samples, not real observations.
- [Four overlays on the prior 729 logarithmic radius addresses](BOUND14_KERR_729_LOG_RADIUS_WITNESS_20261027.csv), 2,916 rows. At every historical Bound 10 areal-radius label, Kerr and Schwarzschild coordinate radii are compared only when `r_+<=r<=200r_g`. All other tidal and proper-clock values are **blank**, not zero.

| Log registry status | chi=0 | chi=0.5 | chi=0.9 | chi=0.99 |
| --- | ---: | ---: | ---: | ---: |
| Exterior modeled and reportable | 26 | 27 | 28 | 29 |
| Inside Kerr outer horizon: not computed | 592 | 591 | 590 | 589 |
| Outside chosen starting position | 110 | 110 | 110 | 110 |
| Formal center 000 sentinel | 1 | 1 | 1 | 1 |
| Total per assumed spin | 729 | 729 | 729 | 729 |

**Important:** The Bound 10 logarithmic radial coordinate is called “areal radius” because its original Schwarzschild meaning was an areal radius. In Kerr that *same numeric value* is explicitly taken as a **Boyer–Lindquist radial coordinate label** for this distinct scenario. The Kerr BL coordinate is **not** itself the intrinsic Kerr areal radius. Source labels are preserved but must not be relabeled as identical physical geometric radii between metrics.

The 24! SJT traversal continues `rank 0 / Gray 000 / station 000`, `rank 1 / Gray 001 / station 001`, and `last / Gray 100 / station 728`. Its closing seam is **logical only** and cannot advance the infaller's proper time or carry a physical object from Sun to Sgr A*.

## Files committed

- [Self-contained interactive observer clock, local tetrad and tidal field](bound14-kerr-falling-frame.html).
- [Equation-based Kerr geodesic and tetrad engine](bound14_kerr_fall_tetrad_core.js).
- [Independent Kerr Riemann and parallel-transport numerical validator](bound14_independent_curvature_validator.js).
- [Four spin-specific proper-time series, each 729 positions](BOUND14_KERR_729_PROPER_CLOCK_SPIN_SWEEP_20261027.csv).
- [Historical logarithmic 729-radius witness with blank unmodelled values](BOUND14_KERR_729_LOG_RADIUS_WITNESS_20261027.csv).
- [Machine-readable audit and source/validation lineage](BOUND14_KERR_TETRAD_AUDIT_20261027.json).

The HTML's four scripts passed compile checks, and a simulated browser DOM exercised start, midpoint, horizon, alternative spin choices, BL-frame horizon guard, and 24! forward/backward/seam and invalid rank, all passing. Real browser rendering and live GitHub Pages deployment have **not** been verified.

## Literature/independent witnesses

- Kerr parallel-transport tetrad and equatorial electric tidal curvature: Camilloni et al., MNRAS 531, 1884 (2024), [published analytic expressions Eq. (28)](https://academic.oup.com/mnras/article/531/1/1884/7667944).
- Xin and Mummery, *Relativistic tidal tensor*, [Phys. Rev. D 113, 044036 (2026)](https://doi.org/10.1103/xdm3-48nb), observer-dependent tidal projections.
- Banerjee et al., [Physics Letters B, 2019](https://doi.org/10.1016/j.physletb.2019.05.048), equatorial Kerr first integrals.
- Marck (1983), *Solution to the equations of parallel transport in Kerr geometry; tidal tensor*, Proceedings Royal Society A.
- GRAVITY Collaboration, [Sgr A* dynamical mass](https://doi.org/10.1051/0004-6361/202142465).

The theory, numerical projection and implementation are **three independent witness lines**. No votes or consensus requirements apply, and lack of direct observation is explicitly preserved.

## Next natural Bound 15 — Horizon-penetrating local frame

Continue the same (E=1,L_z=0,Q=0) Kerr observer through the outer horizon **only after transforming to a horizon-penetrating ingoing Kerr coordinate chart**, with finite observer and tetrad components and independently verified metric/connection transport. Then inspect the classical inner-horizon/Cauchy-horizon gate and instability literature; do not claim a known physical path to the singularity. The separate *magnetic* tidal field and dynamic finite-rod response can be added with measured material assumptions instead of transferring Schwarzschild stress values unchanged.

Freeze: Bound 14 is append-only. **Bounds 01–13 remain unchanged**, with 729 previous observations and the full (24!) symbolic cycle retained.
