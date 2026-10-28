# Natural Bound 13 — Finite material response and independent Kerr spin geometry (2026-10-27)

Evidence: `ITD_BOUND13_FINITE_ROD_AND_KERR_GEOMETRY_20261027`

Status: `SCHWARZSCHILD_1D_MATERIAL_ESTIMATE` + `QUASI_STATIC_BOUNDARY` + `KERR_SPIN_HORIZON_ISCO_COMPUTED` + `MATCHED_KERR_FALLING_TIDAL_TENSOR_NOT_CALCULATED` + `24_FACTORIAL_LOGICAL_ONLY`.

**Append-only successor** to [Bound 12: local tidal Jacobi separation](BOUND12_NATURAL_BOUND_2026-10-27.md). No modifications to Bounds 01–12, the 729 linear Galactic force record, the 729 logarithmic radius registry, the common moving Galaxy frame or the full 24! SJT state cycle.

## Core finding: free-fall tidal separation is not material stress

Bound 12 used **independent freely falling test particles**, each with negligible mass and no elastic attachments. That test-particle calculation does not predict whether a spaceship, a human body, or a rod stretches or breaks.

This bound introduces a **separate**, intentionally idealized 1D uniform rod of length L, mass density rho and Young's modulus E. Its midpoint follows the same E=1 radial Schwarzschild free-fall reference worldline. The ends are traction-free. Assume small deformation and internal stresses have enough time to approach quasi-static balance with the tidal gradient.

In the locally falling orthonormal frame,

    lambda_radial = c^2 r_s / r^3
    lambda_transverse = -(1/2) lambda_radial

For a rod oriented radially, uniform density, and coordinate x measured from its midpoint:

    d sigma_r/dx = -rho * lambda_radial * x
    sigma_r(±L/2) = 0

    sigma_r(x) = rho * lambda_radial * (L²/8 - x²/2)
    sigma_r_max = rho * lambda_radial * L²/8

The transverse-axis compression value `−sigma_r_max/2` in the CSV and viewer is an illustrative *separate axial rod orientation*, not a full three-dimensional elastic stress tensor. The 3D Poisson ratio, anisotropy, geometry and rate-dependent constitutive laws have **not** been supplied.

### Chosen material and wave assumptions, not measurements

The default **steel-like** scenario uses illustrative—not specimen-certified—properties:

| Quantity | Assumed input |
| --- | ---: |
| Density rho | 7,800 kg/m³ |
| Young's modulus E | 200 GPa |
| Yield-stress comparison | 250 MPa |
| Rod length L | 1 meter |
| Maximum wave/tidal timescale ratio | 0.10 |
| Maximum rod length / local geometric scale | 0.01 |

Simple axial-wave speed in a 1D linear-elastic bar is `c_wave=sqrt(E/rho)`. A quasi-static response is not warranted when the wave crossing time `L/c_wave` is comparable with the local tidal timescale `1/sqrt(lambda_radial)`.

The declared applicability checks are:

    q_wave = (L/c_wave)*sqrt(lambda_radial) <= 0.10
    q_local = L/min(r, sqrt(r^3/r_s))    <= 0.01
    sigma_r_max < assumed_yield_stress
    r_stop_classical <= r <= 100*r_s

Both 0.10 and 0.01 are **chosen model-hygiene limits**, not derived universal constants. Yield is treated as a warning proxy, not actual fracture.

## Computed nonrotating Sgr A* material results

From the adopted Sgr A* mass M=4.297 million solar masses (GRAVITY Collaboration 2022) and `r_s≈12.690 million km`:

- At the Schwarzschild horizon, the 1m steel-like midpoint quasi-static tension estimate is **0.54414528 Pa**; each transverse-oriented 1D compression-axis proxy is −0.27207264 Pa.
- The steel-like assumed 250 MPa yield proxy is reached at `r≈16,445.883 km` from the center, inside the `r_s≈12,690,116 km` horizon. For the *specific chosen* E and yield threshold, the quasi-static wave ratio hits 0.10 at **the same radius**. This coincidence follows algebraically from `sqrt(8*sigma_y/E)=0.10`; it is not a physical universal boundary.
- For a 1m aluminum-like illustration (rho=2,700kg/m³, E=70GPa, assumed yield=150MPa) the wave/tidal ratio gate is reached first, at **16,385.420 km**; the stress-based yield proxy would occur later, at about **13,690.832 km**, outside the quasi-static model's validity.
- No real material rupture is established. A proper dynamic model requires time-dependent elasticity, stress-wave propagation, finite strains and body response. The rod is not a black-hole probe demonstrated by observation.

Because the 1-meter finite rod is comparatively short, its own chosen local-length condition remains satisfied until much farther inward than the stress/wave gate; the model first becomes untrustworthy for material physics *well before* the earlier theoretical Planck-curvature boundary.

### The 729 logarithmic registry: blank invalid material values

New [729-row material gate table](BOUND13_729_MATERIAL_GATES_20261027.csv), mapped to *unchanged* Bound 10 logarithmic radii:

| Registry status, default 1m steel-like | Rows |
| --- | ---: |
| All declared material-model assumptions pass | **64** |
| Stress/yield diagnostic exceeds assumed threshold; reportable stress blank | **354** |
| Beyond earlier high-curvature classical gate | **200** |
| Outside chosen 100 r_s starting event | **110** |
| Mathematical center r=0, unresolved | **1** |
| Total | **729** |

The downloadable CSV preserves calculated stress as an explicitly labeled **diagnostic** for invalid regions, but leaves the `REPORTABLE` value cells empty. These are 729 model radii, **not 729 actual stars or solid objects in a galaxy**.

## Independent Kerr channel: exact stationary geometry, unknown falling-body stresses

The real Sagittarius A* may rotate. Its spin was **not measured or fitted** in this bound. Introduce the dimensionless parameter

    chi = c J / (G M²),      0 <= chi <= 1 (assumed here)
    r_g = GM/c²
    a = chi r_g

For the stationary asymptotically flat Kerr vacuum black hole, the **Boyer–Lindquist coordinate** surfaces and circular-orbit boundaries are:

    r_± = r_g [1 ± sqrt(1-chi²)]
    r_ergosurface(theta) = r_g [1 + sqrt(1-chi² cos²theta)]
    r_equator_static = 2 r_g
    Z1 = 1 + (1-chi²)^(1/3) [(1+chi)^(1/3)+(1-chi)^(1/3)]
    Z2 = sqrt(3chi²+Z1²)
    r_ISCO_pro/retro = r_g[3+Z2 ∓ sqrt((3-Z1)(3+Z1+2Z2))]
    A_H = 4 pi [r_+² + a²]
    R_area_equivalent = sqrt(A_H/(4 pi))
    Omega_H = c chi / [2 r_g (1 + sqrt(1-chi²))]

**Do not equate Kerr `r_+` coordinate radius with the intrinsic areal radius.** The equivalent-area radius and the horizon area are separately reported.

### Representative spin scenarios

All values here are model outputs with Sgr A*'s adopted mass, *not observational estimates of its spin*:

| Assumed chi | Kerr horizon r+ (million km; BL) | Prograde ISCO (million km; BL) | Retrograde ISCO (million km; BL) |
| ---: | ---: | ---: | ---: |
| 0 | 12.690 | 38.070 | 38.070 |
| 0.5 | 11.840 | 26.859 | 47.934 |
| 0.9 | 9.111 | 14.726 | 55.312 |
| 0.99 | 7.240 | 9.229 | 56.927 |

The zero-spin limit exactly recovers the Schwarzschild horizon and ISCO. Near extremality, prograde and retrograde stable-orbit boundaries separate significantly.

Kerr geometry contains **frame dragging**, so the observer's local tidal tensors depend on its chosen four-velocity/tetrad. A matched **parallel-transported local free-fall tetrad** with specified Kerr constants of motion `E, L_z, Q` has not been constructed here. Therefore no Kerr local tidal eigenvalues, Kerr finite-rod stresses, or Kerr fracture radii are reported. Substituting a Kerr horizon into the Schwarzschild formula would produce unsupported results.

An algebraic check verifies the Kerr Kretschmann scalar on the equatorial plane at a fixed Boyer–Lindquist coordinate `r` equals `48 r_g²/r^6`, independent of spin; that **does not** establish spin-independent observed tidal forces in arbitrary observer frames.

### Scientific sources

- Bardeen, Press and Teukolsky (1972), Kerr equatorial circular orbits; formulas reproduced in physicist Leo C. Stein's [Kerr calculator](https://duetosymmetry.com/tool/kerr-calculator-v2/).
- Bini and Geralico (2012), [Observer-dependent tidal indicators in Kerr spacetime](https://www.iac.rm.cnr.it/observer-dependent-tidal-indicators-kerr-spacetime?aiac=434).
- Modern Kerr local-frame tidal tensor methods: [Physical Review D, 2026](https://journals.aps.org/prd/abstract/10.1103/xdm3-48nb).
- [GRAVITY Collaboration 2022](https://doi.org/10.1051/0004-6361/202142465) adopted Sgr A* mass; [NIST CODATA](https://www.physics.nist.gov/cuu/pdf/wall_2022.pdf) gravitational constant and Planck scale.

No source has supplied material measurements or solved actual Sgr A* Kerr spin for this computation.

## Computational witness, interactive visualization, and freeze

- [Self-contained interactive material and Kerr viewer](bound13-material-kerr.html): material selectors, rod length, tidal radius and gate control, spin sweep 0–1, Kerr horizon/ISCO plot, and independent SJT 24! Gray address traversal `000→001`.
- [Dependency-free mathematical engine](bound13_material_kerr_core.js): 1D rod static balance, rate and length gates, analytic Kerr geometry, 0-spin/1-spin and equatorial scalar checks.
- [729 finite-material reportability table](BOUND13_729_MATERIAL_GATES_20261027.csv).
- [Ten assumed Kerr spin scenarios](BOUND13_KERR_SPIN_SCENARIOS_20261027.csv).
- [Structured source, calculation and test audit](BOUND13_MATERIAL_KERR_AUDIT_20261027.json).

The committed JS model was fetched and executed: free-end stress balance, yield-radius and wave-gate identities, 1D rod midpoint, Kerr horizon area, zero-spin Schwarzschild and ideal extremal limits, prograde/retrograde ISCO order, and the equatorial Kretschmann checks passed. All four embedded viewer scripts passed syntax checks. A mock-browser interaction test passed steel/aluminum gates, horizon, spin changes, first and last factorial ranks, circular seam and invalid rank guards.

**Not independently verified:** rendered graphics in a real browser, live GitHub Pages deployment, any observed material yielding, actual Kerr falling-frame tidal stress, or Sgr A*'s spin.

## Next natural bound 14

The first missing **physical** link is a Kerr geodesic and an actual free-fall tetrad. Specify the observer's `E, L_z, Q`, integrate the equatorial orbital worldline and parallel-transport its local basis, then compute the electric/magnetic tidal tensor and a properly matched comparison to the nonrotating case. A *separate* time-dependent elastic-rod model would be needed for actual yielding, waves and fracture.

The historical 729-station observations and full 24! logical toroidal traversal are intact. There is no inference that a physical star or gravitational force literally crosses the ring's final→first address seam.
