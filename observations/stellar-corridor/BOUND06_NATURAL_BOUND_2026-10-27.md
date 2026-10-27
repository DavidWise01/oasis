# Natural Bound 06 — R0 reconciliation and independent H I quadrant tracers (2026-10-27)

Record ID: `ITD_MILKY_WAY_BOUND06_R0_HI_20261027`
Status: `PUBLIC_DATA_FOUND` + `FIVE_BY_TWO_HI_TRACER_POINTS_VERIFIED` + `R0_RADIUS_SENSITIVITY_CALCULATED` + `INDEPENDENT_TRACER_DIFFERENCES_OBSERVED` + `FULL_FRAME_REPROCESSING_NOT_DONE`.

Append-only successor to [Bound 05](ROTATION_HOLDOUT_BOUND_2026-10-27.md); the older 729-station Galaxy model and the 38-point red-giant holdout remain **unaltered**.

## Objective
Determine whether the five Eilers (2019) red-giant/model discrepancies at 5.27, 5.74, 6.23, 6.73 and 7.22 kpc disappear when the Sun–Galactic-Center distance is adjusted from the Eilers adopted R0 = **8.122 kpc** to the OASIS model R0 = **8.277 kpc**; then obtain a separate **non-red-giant gas tracer** at the same nominal Galactic radii.

## Three independently traceable witness lines

### A — Eilers et al. (2019) luminous red giants

The original source and model comparison is frozen in [Bound 05](ROTATION_HOLDOUT_BOUND_2026-10-27.md). Eilers inferred the Galactic circular-velocity curve from stellar kinematics, removing the central ~5 kpc due to strong bar-induced nonaxisymmetry. The five selected problem radii (km/s) are 5.27:226.83, 5.74:230.80, 6.23:230.80, 6.73:231.20, 7.22:229.88.

Publication: https://doi.org/10.3847/1538-4357/aaf648
Author-supplied numeric data via Marius Cautun: https://github.com/MariusCautun/Milky_Way_mass_profile/blob/eb747da6b0383f23cfa4e1fc0dfb8f00a857bfac/MW_rotation_Eilers_2019.txt

### B — Neutral hydrogen gas, two Galactic quadrants

Stacy McGaugh's 2018 Galactic rotation model site publishes HI terminal-velocity-derived circular speeds for the first and fourth quadrants, referencing the HI observations of McClure-Griffiths & Dickey (2007 and 2016). The website explicitly states that these tabulations assume **R0 = 8.122 kpc, Theta0 = 233.34 km/s**; their velocities are not raw line-of-sight observations without adopted Galactic rotation and solar reference assumptions.

- Original index: https://astroweb.case.edu/ssm/models/
- Q1 numeric source: https://astroweb.case.edu/ssm/models/RCQ1.dat
- Q4 numeric source: https://astroweb.case.edu/ssm/models/RCQ4.dat
- Scientific context for terminal-point method and cautions: https://www.sciencedirect.com/science/article/pii/S1387647326000126

Five nearest-radius pairs checked on 2026-10-27:

| Eilers R (kpc) | Q1 exact R | Q1 speed (km/s) | Q4 exact R | Q4 speed (km/s) | Q1 source line | Q4 source line |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5.27 | 5.269112 | 233.2783 | 5.268141 | 227.5004 | 340 | 301 |
| 5.74 | 5.742931 | 236.3508 | 5.740324 | 231.6059 | 410 | 369 |
| 6.23 | 6.227924 | 248.7344 | 6.231380 | 244.2637 | 488 | 440 |
| 6.73 | 6.732106 | 243.0092 | 6.731233 | 245.4741 | 579 | 525 |
| 7.22 | 7.220152 | 242.9605 | 7.222034 | 249.9745 | 683 | 627 |

No uncertainties or covariance tables accompanied these source .dat rows. **Do not** run a gas-tracer significance test or assign zero uncertainties. Nearby Q1 and Q4 points correspond to different positions around the Galactic plane and are NOT two measurements of one physical location. Quasi-circular speeds inferred from terminal velocities are also susceptible to spiral streaming, bar perturbations and gas dynamics.

### C — Frozen four-component prediction

From [Bound 04](MW_FIELD_BOUND_2026-10-27.md), fixed at `R0=8.277 kpc`, `v_c(R0)=233 km/s`. Black hole + bulge + Miyamoto–Nagai disk + NFW halo. The model is a smooth axisymmetric midplane approximation with no individually measured stars and no free parameter changed in this test.

## The radius-convention sensitivity boundary

For a **limited demonstration only**, evaluate the *same frozen model* at:
1. **Unchanged:** `R = R_Eilers`
2. **Additive displacement:** `R = R_Eilers + 0.155 kpc`
3. **Proportional rescaling:** `R = R_Eilers * 8.277/8.122`

The published star-coordinate transformation changes *more* than the radius: heliocentric sky position, distance, adopted solar velocities, noncircular motions and the Jeans equation all affect inferred radial circular speed. Neither shortcut above is a complete physical transformation of the original catalogs. It is forbidden to label the adjusted model velocities as **reprocessed Eilers observations**.

The actual source study [Jiao et al. (2023)](https://doi.org/10.1051/0004-6361/202346474) explicitly identifies R0 sensitivity as a major systematic and notes that Eilers used R0=8.122 kpc and solar azimuthal velocity 245.8 km/s.

## Results — no model refit

| Radius | Eilers v | Fixed model v | Fixed-model residual | Residual after +0.155 kpc | Residual after ratio R0 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5.27 kpc | 226.83 | 240.28 | +13.45 | +13.35 | +13.39 |
| 5.74 kpc | 230.80 | 239.82 | +9.02 | +8.76 | +8.84 |
| 6.23 kpc | 230.80 | 238.88 | +8.08 | +7.72 | +7.81 |
| 6.73 kpc | 231.20 | 237.64 | +6.44 | +6.01 | +6.08 |
| 7.22 kpc | 229.88 | 236.24 | +6.36 | +5.90 | +5.95 |

Units km/s. Carry forward Bound 05's nonprobabilistic envelope test `abs(residual)> max(tabulated_sigma_1,tabulated_sigma_2)+v_obs*systematic_pct/100`.

- Unmodified radius: **5/5** outside the simple envelope.
- Additive shift: **3/5** outside; 6.73 and 7.22 no longer exceed.
- Multiplicative scaling: **4/5** outside; 7.22 no longer exceeds.

A change in R0 therefore moves at least one *marginal* residual across a heuristic flagging threshold, but **does not remove the larger mismatch at 5.27–6.23 kpc**. Since these transformed radii are illustrative only, no formal proof that the mismatch survives full galactocentric refitting is claimed.

## Gas vs red-giant second witness

For illustration only (NOT a best-fit physical average), arithmetic mean of the two nearby HI quadrant values vs Eilers speed:

| R (kpc) | Mean HI (km/s) | Eilers RGB (km/s) | Mean HI − RGB (km/s) | Mean HI − model (km/s) |
| ---: | ---: | ---: | ---: | ---: |
| 5.27 | 230.39 | 226.83 | +3.56 | −9.89 |
| 5.74 | 233.98 | 230.80 | +3.18 | −5.84 |
| 6.23 | 246.50 | 230.80 | +15.70 | +7.61 |
| 6.73 | 244.24 | 231.20 | +13.04 | +6.61 |
| 7.22 | 246.47 | 229.88 | +16.59 | +10.23 |

**New observation:** gas and red-giant inferred rotation speeds differ substantially across parts of 6.2–7.2 kpc, with the two gas quadrants themselves differing at the same radius. This makes it inappropriate to attribute every residual to too much gravitational mass or to a universal 1/4 field transfer law without dynamical/nonaxisymmetric analysis.

## Files and reproducibility

- [5 anchored source-line comparisons plus all three model radius treatments](BOUND06_R0_HI_TRACERS_20261027.csv).
- [Full machine-readable source receipts and scope limits](BOUND06_R0_HI_AUDIT_20261027.json).
- [Standalone interactive HTML](bound06.html).

Numerical R0-sensitivity and five-pair comparisons were executed during record creation; original source numbers were checked at the published web table rows. The exact primary H I underlying line profiles, error budgets and orbital geometry were **not independently reprocessed**.

### Witness / containment

```text
[A: RED GIANTS]       5 flagged Eilers radii
        \
         > [MODEL: BULGE+DISK+HALO+BH] > 729 frozen radial stations
        /
[B: HI Q1 || HI Q4]  different local gas tracers; not identical spatial points
        |
     R0 sensitivity 8.122 / 8.277
        |
[C: DIFFERENCE AUDIT]     no quorum, no refit, no invented masses
```

## Next natural bound 07 — Non-circular/azimuthal harmonics

A genuinely testable next step would obtain raw H I longitudes, radial velocities and uncertainties, reconstruct the longitude-to-tangent-point conversion, and test `m=2` bar/spiral streaming or azimuthally split first/fourth quadrant residuals. Use an external gas dataset for validation, and preserve 729 stations as geometric points, not gravitational relays. At the same time, reprocess stellar Galactocentric radii with common R0 and solar-motion assumptions from the original star catalogs rather than treating a radius shift as a full reanalysis.

No claim of Yang–Mills proof, a new force, or Sgr A* mass transmission is established by these measurements.
