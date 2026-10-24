# KET E.V.E. 45 — Be-8 alpha-alpha scattering historical holdout

Executed: 2026-10-24. Target Be-8 ground-state alpha-alpha resonance. Compare historical scattering-derived width estimates against the later higher-energy-resolution alpha-alpha measurement. This is **not** an original fit of raw phase shifts and thus not a newly calculated microscopic width.

Sources:
- TUNL A=8 1974 historical evaluation: https://nucldata.tunl.duke.edu/nucldata/HTML/A%3D8/08Be_1974.shtml
- TUNL A=8 2004 evaluation: https://nucldata.tunl.duke.edu/nucldata/HTML/A%3D8/08Be_2004.shtml

**Test references:** historical effective range analysis Γ=6.14±0.04 eV; earlier three-level R-matrix Γ=5.1±0.4 eV. Later 1992 high-resolution experimental scattering result, documented in 2004 TUNL evaluation: Γ=5.57±0.25 eV. These are published width estimates derived from independent experimental studies; error bars are quoted as reported, without further covariance/systematic analysis.

| Earlier scattering analysis | Earlier Γ (eV) | Later Γ (eV) | Absolute error (eV) | Relative error | Difference / quadrature uncertainty |
|---|---:|---:|---:|---:|---:|
| Effective range | 6.14±0.04 | 5.57±0.25 | 0.57 | 10.23339% | 2.25136 |
| Three-level R matrix | 5.1±0.4 | 5.57±0.25 | 0.47 | 8.43806% | 0.99640 |

Half-lives implied by earlier widths via T_half = ln(2)*ħ / Γ, ħ = 6.582119569e−16 eV s: 7.43058e−17 s (effective range), 8.94584e−17 s (R-matrix). Later width corresponds to about 8.19e−17 s.

**E.V.E. result:** 2/2 comparisons executed, exact arithmetic checks PASS. Earlier effective-range estimate differs at 2.25 combined quoted uncertainties; earlier R-matrix agrees within 1 quoted combined uncertainty. This cannot be used to say KET or an independently fitted interaction accurately predicted Be-8 Γ. It is a *data independence diagnostic*, not a fitted scattering phase-shift benchmark. Fully raw phase-shift data/uncertainty covariance not obtained; fitting and withheld observable prediction remain PENDING.

Log: `historical_holdout.csv` and `results.json` generated in conversation. KET `[stable{(test-zone)}]` preserves classification and measurement provenance. Frozen 184/257 baseline unchanged.

Next target E.V.E. 46: digitize or acquire tabulated independent alpha-alpha differential/phase-shift data, fit a Coulomb-modified effective-range function on one energy interval, evaluate unfit energy interval and its uncertainty band without tuning to the Be8 decay width.
