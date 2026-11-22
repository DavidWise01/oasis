# AETHER-090 — Preemptive Drift Detection and Conditional Reauthorization

**Invariant 090:** Reauthorization requires evidence of present safety; evidence of past safety is insufficient.

### Experiment

20 paired independent synthetic seeds (90001–90020), 90 inspection ticks per seed. Environment is safe at ticks 1–30 (true wrong-sign risk 0.3%), unsafe at 31–60 (7.5%) and recovers at 61–90 (0.3%). The controller is not given the regime changes. Each tick contains 140 labeled audit observations, 150 held-out action outcomes, and for the sentinel controller 80 additional labeled sentinel observations.

The **rolling-only** baseline authorizes when a fixed-time exact one-sided 95% upper binomial bound from the last five audit batches is ≤ 2%. The **sentinel-reauthorize** controller separately flags implausibly high sentinel errors, suspends permission, resets its post-alarm audit history and only resumes after five recent audit batches satisfy the same gate.

### Observed paired outcomes

| Metric | Rolling-only | Sentinel + reauthorization |
|---|---:|---:|
| Safe initial authorization | 94.67% | 94.00% |
| Unsafe authorization | 0% | 0% |
| Safe recovery authorization | 86.67% | 86.00% |
| Wrong authorized actions (all regimes) | 487 | 485 |
| Evidence labels | 252,000 | 396,000 |
| Illustrative cost | 12,730 | 14,210 |

18 of 20 seeds triggered the sentinel alarm on the first unsafe tick; the other two detected on the second. Reauthorization occurred three or four ticks after recovery. But the baseline also abstained throughout the unsafe regime, so the sentinel did **not** improve safety and cost 1,480 more units under the chosen cost model.

The cost model assigns 10 per wrong action, 0.05 per abstained action, and 0.01 per acquired label. These are illustrative, not domain-specific valuations.

### Limitations and next test

The shift (0.3% → 7.5%) is large and sudden. This is not a test of subtle drift. Distinct synthetic samples are independent by construction; no hidden shared ancestry or contaminated labels. Fixed-time statistical confidence does not guarantee safe decisions immediately after a change. The sentinel false-alarm threshold is calibrated for the simulated stationary safe regime only.

**AETHER-091 — Subtle-Drift Value of Warning:** Evaluate smaller changes near the 2% risk threshold; measure early warning benefit and false-alarm cost using matched independent seeds. Admit sentinel monitoring only when it actually reduces expected loss.

[Interactive GitHub Pages lab](https://davidwise01.github.io/oasis/aether/090/) · [Previous AETHER-089](../089/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
