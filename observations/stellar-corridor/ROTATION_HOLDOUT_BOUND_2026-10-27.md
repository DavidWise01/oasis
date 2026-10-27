# Natural bound 05 — Independent 38-bin Galactic rotation comparison (2026-10-27)

Record ID: `ITD_EILERS2019_MW_FIELD_HOLDOUT_20261027`
Status: `INDEPENDENT_PUBLIC_TABLE_FETCHED` + `38_BIN_NUMERICAL_COMPARISON_PASS` + `5_INNER_RESIDUAL_FLAGS` + `NO_MODEL_REFIT` + `SYSTEMATICS_CORRELATED` + `MODEL_EXTRAPOLATION_RETAINED`.

This is an append-only descendant of [Bound 04](MW_FIELD_BOUND_2026-10-27.md). Previously recorded physical assumptions and all 729 stations remain unchanged. **No observational point is rewritten to agree with the model.**

## Public original research and numerical source receipts

- Eilers et al. (2019), *The Circular Velocity Curve of the Milky Way from 5 to 25 kpc*, Astrophysical Journal 871, 120. Primary paper: https://doi.org/10.3847/1538-4357/aaf648 ; preprint https://arxiv.org/abs/1810.09466 .
- Scientific data hosted by Marius Cautun in repository `MariusCautun/Milky_Way_mass_profile`, itself a reproducible Galactic mass-model study: https://github.com/MariusCautun/Milky_Way_mass_profile
- Exact source numeric file: https://github.com/MariusCautun/Milky_Way_mass_profile/blob/eb747da6b0383f23cfa4e1fc0dfb8f00a857bfac/MW_rotation_Eilers_2019.txt
- Source commit (verified by public GitHub API): `eb747da6b0383f23cfa4e1fc0dfb8f00a857bfac`
- Source text blob SHA: `1214ace5da1b1a02688f2edd5e817ec5826fc3a8`
- Source repo SPDX license `GPL-3.0`: https://github.com/MariusCautun/Milky_Way_mass_profile/blob/master/LICENSE
- Original authors report 5–25 kpc circular speed estimates from ~23,000 red giants and an approximately −1.7 km/s/kpc outer decline. They exclude the inner <5 kpc due to bar dynamics.

**Source caveat:** The accessible public table provides radius, velocity, **two separate km/s uncertainty columns**, and a percent systematic error, without disambiguating the meanings of its two identically labeled sigma columns in its one-line header. Both are preserved as distinct `source_sigma_col3` and `source_sigma_col4` rather than inventing their confidence interpretation. The table is from a published-author secondary research repository, not a newly queried catalog.

## Derived, reproducible artifacts

- [38-row externally measured vs modeled residuals](EILERS2019_MODEL_RESIDUALS_20261027.csv). This derived table contains source numbers with credit and a GPL-3.0-or-later redistribution notice; it is not original OASIS observational data.
- [Machine-readable validation gates](EILERS2019_VALIDATION_20261027.json).
- [Independent holdout evaluator](rotation_holdout_validate.py) calling the **unaltered** earlier [four-component generator](milky_way_bound.py).
- [Standalone interactive dashboard](rotation-holdout.html), containing the 38 actual derived comparison rows, point-selectable velocity curves, error envelopes, and residual plot.

The evaluation compared all 38 numerical rows directly. The file `rotation_holdout_validate.py` carries reproduction/self-check instructions; running the Python code with a local or downloaded pinned Cautun data table reproduces and audits results. The numerical source-to-prediction comparison **was performed** in the GitHub write workflow; fresh invocation of committed Python was not independently completed in that environment.

## Mathematical comparison

At each published radius `R_i` use the unchanged four-component potential from Bound 04:
```text
model v_i          = sqrt(R_i × [g_BH(R_i) + g_bulge(R_i) + g_disk(R_i) + g_halo(R_i)])
residual_i         = model v_i − observed v_i
simple envelope_i  = max(sigma_column_3_i, sigma_column_4_i) + observed_i × systematic_percent_i / 100
descriptive flag   = abs(residual_i) > simple envelope_i
```

This **simple envelope** is a practical conservative visual sensitivity threshold, **NOT** a confidence interval, chi-squared significance, or statistically independent combined error model. Reported systematics can correlate across radius. No formal rejection of physical laws, surveys or the model family is asserted.

### Results

| Scope | Observational bins | Outside simple envelope | Mean residual (km/s) | RMS residual (km/s) |
| --- | ---: | ---: | ---: | ---: |
| All 5.27–24.82 kpc | 38 | 5 | +4.52 | 8.63 |
| Inside original 729 station range (5.27–8.19 kpc) | 7 | 5 | +7.51 | 8.03 |
| External extension (8.78–24.82 kpc) | 31 | 0 | +3.85 | 8.76 |
| 5–15 kpc bins | 20 | 5 | +3.32 | 5.02 |
| >15–25 kpc bins | 18 | 0 | +5.86 | 11.37 |

```text
FLAGGED INNER BINS:  five consecutive observations
radius       observed    model      difference    envelope
5.27 kpc     226.83      240.28      +13.45       ±6.45 km/s
5.74 kpc     230.80      239.82       +9.02       ±6.05
6.23 kpc     230.80      238.88       +8.08       ±6.32
6.73 kpc     231.20      237.64       +6.44       ±6.06
7.22 kpc     229.88      236.24       +6.36       ±5.97
```

**Direction of mismatch:** the existing model predicts **too much** circular speed in the 5.27–7.22 kpc inner corridor. This is not caused by increasing individual stellar masses in the observed sample; the model is smooth and contains no assigned catalog-star gravitational masses. The incorrect profile could result from the assumed bulge/disk/halo decomposition, radius convention, kinematic non-circularity, survey systematics, or multiple factors. No unique cause has been established.

In the outer bins, no single point exceeds the loose envelope; this does **not** mean that the outer potential has been precisely validated. At 15–25 kpc the systematic allowance is larger and the predicted curve might still be systematically biased high.

## Independence and unit boundaries

- **Actual holdout:** Bound 04 was normalized to Jiao et al. (2023) near-Sun 233 km/s, not tuned on this Eilers (2019) 38-bin table. They share broader Gaia/APOGEE methodologies, but are different surveys/analyses, not mathematically independent raw data draws.
- **Different R0 convention:** Eilers' analysis uses approximately `R0 = 8.122 kpc`, while the prior model adopts `8.277 kpc`. We leave the Eilers published bin radii unchanged (a first-order comparison), and flag the difference for a future common-coordinate rerun. No false claim of exact matched frames.
- **Out-of-corridor predictions:** the earlier radial-line model only contained 729 samples from the Galactic Center to `R0 = 8.277 kpc`. To compare 31 outer observed bins, the **same analytic potential** was evaluated at greater radii. These are supplementary extrapolations, *not* additional observed corridor stations or objects.
- **Sun calibration vs held-out Sun neighborhood:** the model equals 233 km/s at 8.277 kpc by construction; Eilers' observed value around 8.19 kpc is 228.86 km/s. This cannot be called agreement simply because the same model matches its original 233 km/s calibration.
- **No 1/4 step inheritance:** a point-source `g∝1/r²` identity does not describe the total Galactic bulge, disk or halo acceleration. Do not combine catalog stars into a 9/9 physical relay.
- **No proof of dark-matter abundance or Yang–Mills mass gap:** curve comparisons alone cannot uniquely distinguish competing matter distributions or quantum-field-theory proofs.

## Three independent witnesses, no quorum

```text
A :: Observational inference — Eilers 2019 / Cautun hosted binned data
B :: Fixed predictive model — Bound 04 bulge + disk + halo + BH
C :: Difference audit — 38 residuals with five consecutive inner flags

PAST     retain the observed source values and their original uncertainty columns
PRESENT  report mismatches and the boundaries of the error heuristic
FUTURE   compare independent sky tracers and common-R0 coordinate transforms
```

No vote, no quorum, no retroactive alteration of evidence.

## Next natural bound (06) — Resolve or preserve the inner residual

1. Reexpress the external rotation-curve radii under a common adopted `R0` and study the sensitivity of the inner five residuals.
2. Evaluate separate published tracer families (e.g. masers, APOGEE/Gaia DR3), including non-circular streaming from the Galactic bar, in out-of-sample radial bins.
3. Do not change the existing 5/60/35 bulge/disk/halo weights to suppress these five flags unless the changed model becomes a **new identified candidate** and a distinct independent holdout is reserved.
4. Use the tracer model, observational uncertainty and force direction to decide which gravitational-field assumption needs revision—not a 729-slot numerical identity.
