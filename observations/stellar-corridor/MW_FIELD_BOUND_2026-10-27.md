# Physical bound 04 — Midplane bulge + disk + halo + Sgr A* field (2026-10-27)

Record ID: `ITD_MILKY_WAY_729_MULTI_COMPONENT_FIELD_20261027`
Status: `CALCULATED_729_MODELED_RADIAL_STATIONS` + `SOLAR_CIRCULAR_SPEED_CLOSURE_PASS` + `POINT_MASS_QUARTER_RULE_PASS` + `CENTER_UNDEFINED` + `MODEL_EXTRAPOLATION_NOT_DIRECT_MEASUREMENT` + `STAR_MASS_CATALOG_PENDING`.
Append-only successor to [Physical bound 03](FIELD_BOUND_2026-10-27.md). No earlier evidence was overwritten.

## Physical target

Traverse 729 equally spaced **numerical** stations from Sgr A* to the Sun along the **Galactic midplane radial coordinate** `R`. This is a model of the **inward radial field** on an axisymmetric Galactic plane—not a survey claiming 729 physically aligned stars, not a real force chain or a measurement of 729 individual stellar masses.

## Data and executable record

- [729 calculated positions with separated forces](SGRA_EARTH_729_MW_COMPONENTS_20261027.csv)
- [Machine-readable parameters, checkpoints and limitations](SGRA_EARTH_729_MW_MODEL_20261027.json)
- [Python 3 standard-library reproducible generator](milky_way_bound.py)
- [Interactive 729-station comparison](field-bound-four-component.html)
- Prior star-catalog and incomplete-live-Gaia provenance records remain unmodified.

## Sources (facts distinguished from model assumptions)

1. **Bovy (2015), galpy**: `MWPotential2014` consists of a `PowerSphericalPotentialwCutoff` bulge with `alpha=1.8`, cutoff 1.9 kpc; Miyamoto–Nagai disk `a=3.0` kpc and `b=0.28` kpc; NFW halo scale radius 16 kpc. Normalized fractional circular **radial force** contributions at its reference point: bulge 0.05, disk 0.60, halo 0.35. The published reference is **8.0 kpc at 220 km/s**. Source https://docs.galpy.org/en/v1.12.0/tutorials/potentials/milky_way_potentials.html ; paper https://doi.org/10.1088/0067-0049/216/2/29 .
2. **Jiao et al. (2023)**: `v_c(R0)=233±7 km/s` estimated near the Sun from stellar motions. https://doi.org/10.1051/0004-6361/202346474 .
3. **GRAVITY Collaboration (2022)**: `R0=8277 pc`, `M(Sgr A*)=4.297×10^6 M_sun` as selected central values. https://doi.org/10.1051/0004-6361/202142465 .

**This implementation is a re-normalized, galpy-inspired model, NOT the exact canonical galpy MWPotential2014 model and NOT a claim to have executed the galpy package.** All three distributed components are re-normalized to the *remainder* of the Sun's inward reference acceleration after subtracting the known black-hole contribution. This yields exactly 233 km/s by design, so calibration closure must not be presented as an independent validation against additional astronomical data.

## Equations

Set `P(s,x)` to the regularized lower incomplete gamma function:

```text
R0 = 8277 pc; v0 = 233 km/s
alpha_b = 1.8; s = (3-alpha_b)/2 = 0.6; rc_b = 1900 pc
a_disk = 3000 pc; b_disk = 280 pc; a+b = 3280 pc
rs_halo = 16000 pc

bulge_force_shape(R) ∝ P(0.6, (R/1900)^2) / R^2
disk_force_shape(R)  ∝ R / [ R^2 + (3280)^2 ]^(3/2)
halo_force_shape(R)  ∝ [ln(1+R/16000) − (R/16000)/(1+R/16000)] / R^2
BH_force(R)          = G M_BH / R^2

reference_total      = (233000 m/s)^2 / (8277 pc in meters)
reference_external   = reference_total − BH_force(R0)
bulge(R)             = .05 * reference_external * bulge_shape(R) / bulge_shape(R0)
disk(R)              = .60 * reference_external * disk_shape(R) / disk_shape(R0)
halo(R)              = .35 * reference_external * halo_shape(R) / halo_shape(R0)
inward_total(R)      = bulge(R)+disk(R)+halo(R)+BH_force(R)
v_c_model(R)         = sqrt(R * inward_total(R))
```

Units of the force shapes are arbitrary until normalized; accelerations output in SI m/s². The NFW halo uses `ln(1+x)-x/(1+x)` and the gamma-profile bulge is computed with a numerical series/continued-fraction method. The Miyamoto–Nagai disk is evaluated only in the **z=0 plane**. Hence the total inward radial acceleration is the sum of positive component magnitudes at that midplane coordinate; this is not a general 3D vector sum.

## Numerical witness checkpoints

| Radius (pc) | BH acceleration (m/s²) | Bulge | Disk | Halo | Total inward (m/s²) | Model v_c (km/s) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 11.37 | 4.633e-9 | 1.355e-8 | 3.503e-12 | 1.309e-10 | 1.832e-8 | 80.17 |
| 1,000 | 5.989e-13 | 3.412e-10 | 2.697e-10 | 1.208e-10 | 7.322e-10 | 150.31 |
| 4,140 | 3.494e-14 | 4.236e-11 | 3.055e-10 | 9.609e-11 | 4.440e-10 | 238.16 |
| 8,277 (Sun) | 8.742386e-15 | 1.062773e-11 | 1.275328e-10 | 7.439411e-11 | 2.125633e-10 | 233.00 |

Numbers derived from the explicit adopted model, **not** measured independently at the listed radii. The relatively large inner-bulge contribution is sensitive to the assumed extrapolated density power law and may be unrepresentative of actual inner-Galactic stellar motions.

At Sun, approximate breakdown of total inward acceleration:
- central BH: `0.00411284%` (approximately 1 in 24,314);
- bulge: `~4.99979%` of total;
- disk: `~59.99753%` of total;
- halo: `~34.99856%` of total.

The last three are **assigned model normalization contributions**, not independently measured proportions of mass.

## Validation performed in numerical model generation

- Regularized gamma `P(0.6, (1000/1900)^2)` agreed with reference `0.4685563844016277` to 1e-12.
- `g_total(8277pc) = v_c²/R0` and `v_c_model(8277pc) = 233km/s` to roundoff.
- Fixed-M black-hole term at `R0/2` exactly 4× `g_BH(R0)`; at `2R0` exactly 1/4× `g_BH(R0)`.
- Exactly `729` station rows, first station at `R=0` **undefined/blank**, and `728` finite positive-field samples.
- Individual measured stellar mass contribution column remains empty; no invented masses, solar speeds, or missing observations.

Note: these checks were executed in the numerical generator used to write the CSV. The committed `milky_way_bound.py` separately includes corresponding assertions and re-generation capability, but an independent fresh Python invocation is not claimed in this record.

## Invariants / interpretation gates

1. **No one-to-one star correspondence:** 729 is the number of analytic radial **sampling locations**, not stars on a literal linear chain and not an empirical force network.
2. **No quarter-force inheritance law:** the user's `1/4 × 4 = 1` applies to inverse-square point-source magnitudes under specific mass/distance ratios. Distributed disk, bulge and halo profiles are NOT all inverse-square functions.
3. **No direct 4D gravitational solution:** `[({})]`, eight manifolds and toroids may annotate the architecture; none of these assumptions produces general relativity, a black-hole field solution, or Yang–Mills mass-gap evidence.
4. **Do not interpret radius zero:** black-hole point-source acceleration diverges at R→0, and weak-field Newtonian interpretation fails near its horizon; the station at exactly R=0 is excluded.
5. **No astrophysical validation away from Sun:** model calibration is local. In the inner Galaxy there is a nonaxisymmetric bar, central molecular zone, nuclear stellar populations and interstellar matter. The adopted potential cannot certify measured stellar orbits at arbitrary radius.
6. **No direct additive star-count inference:** decomposed galactic radial acceleration contains distributed fields that cannot be reconstituted from a sparse bright-star sample without a selection function and mass posterior.
7. **No uncertainty falsely computed:** the adopted parameters are fixed values, not a posterior or a band of errors. To fit real data, specify independent rotation-curve constraints at multiple radii and propagate source/model uncertainties.

## Next scientific bound

**Out-of-sample rotation-curve residuals and an inner-Galaxy reality check.** Compare the predicted `v_c(R)` against public measured tracers in several noncalibration radial bins (e.g. 5, 6, 7, 9, 10+ kpc), propagate uncertainties, and flag extrapolated/poorly constrained regions. Do not refit parameters to every validation point without keeping an independent holdout set. Incorporate bar/noncircular motions before treating the 0–4 kpc model as physical truth.

The three-witness boundary remains: catalog observation / physical model / external measurement. No votes or quorums, only mismatches and their provenance.
