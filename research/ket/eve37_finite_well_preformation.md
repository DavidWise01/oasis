# E.V.E. 37 — Finite nuclear well, assault frequency and alpha preformation

Executed 2026-10-23 using NUBASE2020 source `PavelStransky/NuclearProperties/nubase_4.mas20.txt`. Source evaluation Kondev et al., Chinese Physics C 45 (2021), 030001. Reference models: https://cpc.ihep.ac.cn/article/doi/10.1088/1674-1137/ad3d4b and https://zgwlc.xml-journal.net/article/doi/10.1088/1674-1137/ac7fe8 .

**Cohort** 175 alpha-dominant ground-state nuclides, requiring unflagged ground-state mass excesses of parent, daughter, two adjacent isotopes, He4; positive alpha Q <20 MeV and available numeric alpha branch; y=log10(T_total seconds)-log10(alpha branch fraction). 5 contiguous sorted-Z held-out folds, test counts 9,13,51,77,25.

**Approximate physical model:** external Coulomb barrier from R = 1.2*((A−4)^(1/3)+4^(1/3)) fm to b=2*(Z−2)*1.43996448/Q fm; closed-form WKB Coulomb action and exp(−2S). Internal well treated as constant −40 MeV (square well) to set particle velocity and estimated assault frequency nu=v/(2R); **this particular approximation does not solve a smooth finite-potential turning-point problem**. Preformation probabilities assumed: even-even .43, odd mass .35, odd-odd .18, drawn as phenomenological examples from published models. Talpha = ln(2)/(nu * S_alpha * P_wkb).

| Model | MAE log10(s) | RMSE log10(s) |
|---|---:|---:|
| v35 empirical barrier, shell gap, logQ and composition refit | 0.506163168 | 0.672228862 |
| v37 regression with physical WKB log10 action, shell gap and composition | **0.434431780** | **0.639850662** |
| Direct finite-well assault + parity preformation + external WKB (no outcome fitting) | 0.834605277 | 1.044059179 |
| Direct well and WKB, S_alpha=1 | 1.291200475 | 1.452381478 |

**Caveats:** The first two models include ridge-fitted coefficients using training subsets and are holdout predictions. The last two are direct phenomenological formulas and do not fit targets (the parity factors themselves originate in prior studies). Distinct model categories should not be conflated. Predictions are in log10 seconds; 1.0 error is factor ten. Parameter uncertainty and data uncertainty have not been propagated; this is not a validated microscopic preformation estimate. The direct physical model predictions are biased low by 0.8346 and 1.2912 log10 seconds, respectively. The calibrated WKB model is similar but not numerically identical to v36 because the feature basis was changed and refitted. Spin/parity selection for individual alpha-daughter transitions not re-evaluated here.

**KET result:** `[stable{(test-zone)}]` maintains empirical validation separately from model hypotheses. Stable prior kernel and frozen 184/257 reference unchanged. Next target: fit only allowed global preformation calibration on training folds, test parameter/region sensitivity and confidence intervals; proceed to smooth nuclear potential when numerical code is feasible.
