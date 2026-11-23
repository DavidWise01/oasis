# AETHER-123B — Identity-preserving bounded calibration

**Synthetic PASS** on 540 paired episodes (60 new seeds × nine regimes), 12,960 ticks per policy; **7,560/7,560** deterministic checks.

Four opaque, non-saturating interior pilots at input counts 32, 96, 160, 224 validate an affine gain/offset model. The first three fit the model; the fourth checks residual. Admit only if 0.8≤gain≤1.2, |offset|≤16, residual≤1 and no pilot clipping. An exact identity fit passes measurements unchanged; otherwise corrected error counts receive +3 uncertainty margin before a one-sided Clopper-Pearson risk bound.

In the synthetic test, both controllers made 0 unsafe authorizations; safe ACT **1,379→4,239** while illustrative total cost increased **364,024.0→431,524.8** due to calibration work. Clean ACT **839→839** and hazard-shift ACT **480→480**. Negative-offset clipping, nonlinear response, and hard saturation remained HOLD. The failed AETHER-123 initial test is retained, not overwritten.

This is not independent hardware calibration or safety proof: the affine assumption, calibration truth and opaque same-path delivery are trusted in the model. A sensor that recognizes probes or behaves differently on low-valued risk readings can evade the gate. Run `python experiment.py` with NumPy and SciPy.
