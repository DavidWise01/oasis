# AETHER-095 — Evidence-Efficient Conditional Promotion

**Invariant 095:** Permission to adapt must remain local to the evidence supporting it, and reversible when that evidence no longer applies.

## Scope and method

The previous AETHER-094 rejected global adoption of a learned sentinel schedule. This experiment separately evaluates six simulator regimes: stable, step, ramp, burst, asymmetric burst, and oscillatory shift.

The frozen learned policy purchases 80 sentinel labels only when the audit state is **uncertain**. Rolling-only purchases no sentinels. Both use the same 140 audit labels and 150 independently held-out action outcomes per tick. Each episode runs 72 ticks with randomized environmental change points and risk levels.

**Three disjoint evidence sets** per regime:
- Discovery: seeds 95001–95024. Propose learned policy only if discovery average costs less than rolling-only.
- Validation: seeds 95101–95160. Require positive one-sided bootstrap lower bound on *paired seed-level savings*, using Bonferroni alpha=0.05/6 across six regimes (10,000 resamples).
- Holdout: seeds 95201–95260. Evaluate only after the promotion table is frozen.

The simulator provides regime context labels. **This experiment does not yet learn or validate a live regime classifier or demonstrate mid-episode revocation.** Conditional use requires correct external context recognition, not inference from the held-out outcomes.

## Validation gates

| Regime | Discovery candidate? | Validation lower bound | Promoted? |
|---|---|---:|---|
| Stable | No | -4.400 | No |
| Step | Yes | -1.055 | No |
| Ramp | No | -8.927 | No |
| Burst | Yes | +3.230 | **Yes** |
| Asymmetric burst | Yes | -10.076 | No |
| Oscillatory shift | Yes | -8.222 | No |

## Independent holdout results

| Regime | Rolling-only cost | Conditional cost | Savings |
|---|---:|---:|---:|
| Stable | 26,220.5 | 26,220.5 | 0 |
| Step | 32,070.5 | 32,070.5 | 0 |
| Ramp | 31,838.0 | 31,838.0 | 0 |
| Burst | 33,453.0 | **32,208.7** | **1,244.3** |
| Asymmetric burst | 30,680.5 | 30,680.5 | 0 |
| Oscillatory shift | 33,053.0 | 33,053.0 | 0 |
| **All** | **187,315.5** | **186,071.2** | **1,244.3 (0.664%)** |

Burst-regime wrong actions were 1,821 under rolling-only and 1,529 under the learned sentinel. Authorized inspection ticks decreased from 3,094 to 2,999. The policy is deliberately withheld in the five other regimes.

Cost = 10 × wrong actions + 0.05 × withheld actions + 0.01 × acquired labels, in illustrative units.

## Reproduce

Requires NumPy and SciPy.

```bash
python aether/095/experiment.py
```

Outputs: `seed_results.csv` (all discovery, validation, holdout episodes), `certification.csv`, `holdout.csv`, `results.csv`, and `manifest.json`. The version-specific directory is append-only; earlier AETHER bounds remain unchanged.

## Limitations

- Artificial Bernoulli risk observations, not measured physical systems.
- Regime identity is supplied by the simulator; real-world context recognition and source-ancestry checks remain untested.
- Promotion is selected before holdout evaluation, but the six regimes belong to one simulator family.
- Bootstrap lower bounds are not distribution-free, anytime-valid guarantees under adaptive monitoring.
- **Reversibility is an architectural requirement, not yet an observed within-run behavior.** Revoke permission upon context invalidation in the next iteration.

[GitHub Pages interactive report](https://davidwise01.github.io/oasis/aether/095/) · [Previous AETHER-094](../094/)

## Next natural bound — AETHER-096: Context Detection and Revocation Latency

Replace simulator-provided regime labels with evidence-derived context classification. Introduce mid-run regime changes, measure context false matches, permission leakage, revocation delay, and conditional recovery. Require a reliable fallback whenever the context certificate expires or evidence becomes contradictory.

**Invariant 096 candidate:** A permission tied to a context must end when the evidence establishing that context ends.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
