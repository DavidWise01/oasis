# AETHER-099B — Conditional Sensor Revocation

**Phase II Turn 4 of 8: ACCEPTED under the prespecified synthetic acceptance gate (50% complete).**

## Objective and repair

AETHER-099's always-on sensor reduced unsafe authorizations but incurred high cost and 3,885 additional safe HOLDs, especially under a decoy signal. AETHER-099B preserves that failed result in `../099/` and tests a constrained evidence-purchasing rule.

**Diodic governing rule:** The single rolling audit controller retains authority. Only when the rolling upper bound is ≤2% **and** current audit has ≥2 errors does it purchase an additional proxy reading. A proxy ≥2.0 revokes authorization for that tick. Otherwise the original audit's ACT/HOLD decision remains. No independent controller votes, no hidden true regime input, and no retroactive rewriting.

## Separate development and final evaluation

- **Development**: 40 seeds (99101–99140) for each of 3 synthetic environments. Eighteen predeclared candidate rules vary current audit anomaly threshold (1–3), proxy threshold (1.5, 2, 2.5) and extra cooldown (0–1 tick). Choose the least expensive rule **that passes the three gates on development seeds**, then freeze it.
- **Final holdout**: 80 untouched paired seeds (99201–99280) for each of abrupt, gradual, and decoy shifts; 100 ticks per seed, **24,000 ticks per policy**.
- Fixed selected parameters: **audit count ≥2, proxy ≥2.0, cooldown 0**.
- Three policies share the same generated audit/error/proxy outcomes within each paired seed: rolling-only, previous continuous sensor, conditional sensor.
- 140 audit labels and 150 held-out decision outcomes per tick. Proxy requested only when gate qualifies. Risk truth available only for evaluation, not for decisions.

## Held-out results

| Policy | Unsafe ACT ticks | Safe HOLD ticks | Wrong outcomes | Sensor probes | Total modeled cost |
|---|---:|---:|---:|---:|---:|
| Rolling-only | 42 | **978** | 8,958 | 0 | 159,600.0 |
| Continuous sensor | **2** | 5,056 | 6,687 | 24,000 | 172,575.0 |
| **Conditional sensor** | **3** | 1,311 | **8,464** | **1,342** | **157,718.4** |

Relative to rolling-only: **92.86% fewer unsafe authorizations (42 → 3)**; **333 additional safe holds = 1.6584% of safe ticks**; **1,881.6 cost units saved**. Thus all gates pass: ≥20% fewer unsafe ACT ticks, no increase in total cost, ≤5% additional safe HOLDs.

Under the decoy regime alone, conditional sensor is **more expensive than rolling-only** (47,529.2 vs 46,857.5). This is preserved as a residual counterexample rather than hidden by aggregate success.

**Cost formula:** 10 × wrong action outcome + 0.05 × withheld action + 0.01 × acquired audit label + 0.2 × purchased sensor probe. All values are illustrative.

## Reproduce

```bash
python aether/099b/experiment.py
```

Requires NumPy and SciPy. Regenerates `development_options.csv`, `results.csv`, `seed_results.csv`, `tick_audit.csv`, `counterexamples.csv` and `manifest.json`. No held-out seed is used to pick policy parameters.

## Limits

- Synthetic Bernoulli audit outcomes and an artificially defined normally distributed proxy. New random seeds are not a new physical sensing mechanism.
- The controller sees the current audit and proxy before making a decision in the same tick. Delayed signals need separate testing.
- Proxy and audit roots are independent by construction, not externally validated.
- Fixed-time confidence bounds describe past observation windows, not guaranteed instantaneous safety after drift.
- Passing all gates shows a narrow experimental result, not universal economic optimality or field readiness.

[Interactive GitHub Pages-ready report](https://davidwise01.github.io/oasis/aether/099b/) · [Failed AETHER-099](../099/) · [Phase tracker](../PHASE-II-STATUS.md)

## Next natural bound — AETHER-100: Fresh-Evidence Conditional Reauthorization

Measure how quickly revoked decisions can resume using fresh evidence, preventing stale calibration inheritance and oscillatory HOLD/ACT behavior. The governing selector remains deterministic. New bound earns phase progress only when it passes.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
