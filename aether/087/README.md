# AETHER-087 — Tail-Aware Evidence Transfer

**Invariant 087:** Similarity in ordinary behavior does not establish equivalence under consequential failures.

The three-way synthetic comparison uses 12 seeds, six environmental regimes, 16 batches/regime, and 350 independent held-out observations per batch (403,200 test observations per policy).

| Policy | Authorized | Wrong | Conditional wrong rate |
| --- | ---: | ---: | ---: |
| Local only | 318,708 | 146 | 0.046% |
| Median gate | 326,760 | 271 | 0.083% |
| Tail aware | 318,619 | 141 | 0.044% |

Tail-aware transfer checks median, 90th and 98th absolute-residual quantiles, signed mean, and counts of large positive/negative residuals before permitting historical sample pooling. A separate 650-observation audit determines whether candidate radius clears the heuristic 2% conditional wrong-sign risk bound. Held-out cases never participate in calibration or certification.

**Critical failure mode:** On asymmetric outliers, median transfer yields 247 wrong authorizations versus 117 for tail-aware and local-only. The improvement largely comes from rejecting unsafe transfer rather than creating an advantage over fresh local data. The tail-aware controller authorizes fewer decisions.

**Limitations:** Simulation only; thresholds, normal-approximate confidence tests, and adaptive candidate selection do not certify conditional risk under all shifts. No real instrument validation.

[Interactive GitHub Pages report](https://davidwise01.github.io/oasis/aether/087/) · [Previous bound](../086/)

Next AETHER-088: sequential conditional-risk control under repeated monitoring, testing optional stopping and non-independent audit evidence.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
