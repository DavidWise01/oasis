# Natural Bound 07 — Azimuthal mirror asymmetry and bounded m=2 field (2026-10-27)

**Evidence ID:** `ITD_BOUND07_MIRROR_ODD_M2_20261027`

**Status:** `OBSERVED_HI_Q1_Q4_SOURCE_VALUES_RECHECKED` + `MIRROR_ODD_SIGN_REVERSAL` + `MODELED_729_RADIUS_TWO_FORCE_COMPONENTS` + `GRADIENT_DIFFERENCE_VALIDATED` + `TOY_POTENTIAL_ONLY_NOT_FITTED` + `NO_ERROR_COVARIANCE`.

Append-only successor to [Bound 06](BOUND06_NATURAL_BOUND_2026-10-27.md); Bound 04's 729 radial samples, Bound 05's Eilers 38-bin comparisons, and Bound 06's five Q1/Q4 sample pairs remain unchanged.

## Goal / distinction

The earlier analysis mapped *inward radial acceleration* along a straight Galactic-center-to-Sun axis. A flattened barred Galaxy generically creates both radial and tangential components:

```text
g = g_R(R,φ) e_R + g_phi(R,φ) e_phi

  g_R    = −∂Phi/∂R
  g_phi  = −(1/R) ∂Phi/∂phi
```

**Important:** different H I gas rotational speeds in two sky quadrants are not direct measurements of these two acceleration components. Gas moves noncircularly and with pressure, spiral and bar streaming. The recorded gas decomposition below is observational **velocity**, while the four-component baseline and toy perturbation below are **models**.

## Witness A — Public H I observations, no inferred masses

Original primary source links, independently checked:
- McGaugh public Milky Way model site https://astroweb.case.edu/ssm/models/ — first/fourth Galactic quadrant rotation tables normalized to `R0=8.122 kpc`, `Theta0=233.34 km/s`.
- Q1 primary numeric table https://astroweb.case.edu/ssm/models/RCQ1.dat, original exact source lines 340, 410, 488, 579, 683.
- Q4 primary numeric table https://astroweb.case.edu/ssm/models/RCQ4.dat, original exact source lines 301, 369, 440, 525, 627.
- The source credits the neutral-hydrogen terminal velocity observations of McClure-Griffiths and Dickey (2007; 2016). Those source tables are themselves transformed inferred circular speeds, **not** raw gas line-of-sight measurements.

Observed mirror parity at nearest corresponding Galactic radii:

| R from GC, kpc | Q1 speed km/s | Q4 speed km/s | Even (mean) km/s | Odd (half difference) km/s |
| ---: | ---: | ---: | ---: | ---: |
| 5.27 | 233.2783 | 227.5004 | 230.38935 | +2.88895 |
| 5.74 | 236.3508 | 231.6059 | 233.97835 | +2.37245 |
| 6.23 | 248.7344 | 244.2637 | 246.49905 | +2.23535 |
| 6.73 | 243.0092 | 245.4741 | 244.24165 | −1.23245 |
| 7.22 | 242.9605 | 249.9745 | 246.46750 | −3.50700 |

```text
v_even(R) = (v_Q1(R)+v_Q4(R))/2
v_odd(R)  = (v_Q1(R)-v_Q4(R))/2
```

The odd component changes sign in the **sampled interval 6.23–6.73 kpc**. A straight-line interpolation between these two points crosses at approximately **6.5523 kpc**, but it is not a statistically constrained physical transition radius. The source tables lack a covariance or error budget for this pairwise exercise, so significance is **unknown**.

For illustrative circular tangent-point geometry only, with the *gas tables' own* R0=8.122kpc, the near/far mirrored galactocentric polar angles are `φ=±arccos(R/R0)`. This yields `|φ|≈49.56°,45.01°,39.91°,34.02°,27.24°` for the five pairs (using the mean of the two actual Q1/Q4 tabulated radii). The points are not identical physical locations in 3D and no uncertainty is attached to these angles.

If and only if a restrictive m=2 *velocity* ansatz `v(R,φ)=v0(R)+A(R)cos(2φ)+B(R)sin(2φ)` is imposed, the mirror-odd part `v_odd=B(R)sin(2φ)` and `B_eff=v_odd/sin(2φ)` can be computed. **B_eff is a conditional velocity coefficient, not a bar potential strength, force estimate or separately measured harmonic**. Two mirror samples cannot identify the isotropic part and the even cosine harmonic independently.

The CSV also includes `(v_Q1²-v_Q4²)/R` as a **conditional centripetal proxy** to aid dimensional checks; it is **not** observed acceleration or a force difference.

## Witness B — Frozen 729-station radial force

The source radial acceleration in SI units is read unchanged from:

[Bound 04: model components per station](SGRA_EARTH_729_MW_COMPONENTS_20261027.csv).

There remain exactly **729 model radii**, of which the first (Sgr A* point-source mathematical center) has undefined acceleration. At every finite station, the previous radial inward baseline remains unchanged in its source file.

No published cataloged stellar mass is assigned to any station, and no dark-matter profile is refit to the gas velocities.

## Witness C — Separate explicitly hypothetical m=2 potential

Motivation: published Galactocentric maps from Gaia DR3 reveal a quadrupolar / bisymmetric streaming field consistent with barred-Galaxy dynamics. Independent references:
- E. Vislosky et al. (2024), *Gaia DR3 data consistent with a short bar connected to a spiral arm*, MNRAS 528:3576–3591, https://doi.org/10.1093/mnras/stae083 .
- J. Shen and X.-W. Zheng (2020), *The bar and spiral arms in the Milky Way*, Research in Astronomy and Astrophysics 20:159, https://doi.org/10.1088/1674-4527/20/10/159 (review bar orientation ~25–30°, bar length around 5kpc).
- galpy documentation, DehnenBarPotential / cosine mφ disk potentials: https://docs.galpy.org/en/latest/reference/potential.html .

For a visual scenario, choose—not fit—`ε=0.02`, `v_ref=233 km/s`, `R_b=4.5 kpc`, `φ_bar=25°`, and

```text
f(R) = (R/4.5kpc)^2 × exp[1 − (R/4.5kpc)^2]

deltaPhi(R,φ) = ε × v_ref² × f(R) × cos[2(φ − φ_bar)]

delta_gR       = − ε v_ref² f'(R) cos[2(φ−φ_bar)]
delta_g_phi    = + 2 ε v_ref² f(R) sin[2(φ−φ_bar)] / R

signed_total_gR = − g_bound04(R) + delta_gR
signed_total_g_phi = delta_g_phi
```

where derivatives are converted to meters so accelerations are SI m/s². This is an elementary, time-static, approximate bisymmetric potential. Its mathematical quadrupole shape should **not** be read as independent confirmation of a specific Galactic-bar mass, exact pattern speed, or a self-consistent Milky Way orbit distribution. In particular, adding nonzero ε changes the calibrated field at the Sun, which must not be silently claimed to remain matched to 233km/s.

### Analytical and numerical checks

Numerical generation checked:
- Original 729 baseline model radii and central undefined first row retained.
- New 729-row perturbation table has 728 finite model radii, and blank Q1/Q4 sample geometry outside the H I tangent condition `R>8.122kpc`.
- Two finite-difference checks of the potential's radial and azimuthal partial derivatives matched direct force formulae (relative tolerance below 10⁻⁸ at test radius 6kpc, φ=0.4rad).
- ε=0 produces zero added bar forces, and halving ε halves the perturbative force exactly.
- Five observed odd components retain `+++−−` signs.
- These are algebraic/program implementation checks, not an observational fit or physical validation of the potential. The Python script contains reproducibility assertions but its standalone invocation was not independently verified at the time of committing the JS-generated data.

## Committed, separate artifacts

- [Five H I mirror even/odd diagnostics and source-line anchors](BOUND07_HI_MIRROR_ODD_20261027.csv).
- [729 sampled radial plus azimuthal hypothetical perturbation entries](BOUND07_729_M2_POTENTIAL_SCENARIO_20261027.csv).
- [Parameter / provenance / scope record](BOUND07_M2_AUDIT_20261027.json).
- [Reproducible Python using *frozen* source files](azimuthal_bound07.py).
- [Standalone interactive GitHub HTML with all 729 baseline values embedded](bound07.html).

The interactive HTML keeps observational 5-point data visually separate from the adjustable 729-position theoretical scenario. It has controls for ε=0,0.01,0.02,0.05, bar orientation 20°,25°,30°, and model station 2–729. Arrows are normalized *field direction*, not particle trajectories or force magnitude.

## Scientific disposition

The H I mirror velocity asymmetry, including sign reversal in the five preselected samples, is **observed evidence for non-identical derived kinematics**, not a unique causal identification of bar gravitational forces. Independent Gaia DR3 evidence supports bar-related nonaxisymmetric streaming as a plausible class of explanation. The toy ε=0.02 potential is a **candidate visualization only** and has not been fit to these velocities. The model remains falsifiable using a larger survey with errors and full galactocentric geometry.

## Next natural bound 08 — Identify the force from full kinematics

Acquire a publicly archived **Gaia DR3 full 3D radial/tangential velocity map**, with spatial covariance and uncertainties. Compare the **odd vs even m=2 harmonics in measured stellar velocity at more than two azimuths per radius**, including solar-motion and R0 consistency. Reserve spatial holdout sectors. Only then estimate an azimuthal **potential**, if supported by a dynamical Jeans/orbit model with gas pressure and velocity-dispersion effects. Revisit the 729 radial sampling system without equating sampling nodes to actual stars.

Three witnesses report independent claims; **no agreement or quorum is imposed**.
