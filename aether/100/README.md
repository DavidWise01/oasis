# AETHER-100 — Fresh-Evidence Conditional Reauthorization

**Phase II · Turn 5 acceptance: FAILED. Phase remains 4/8 = 50%.**

## Goal

Reauthorization after suspension must rely on fresh, post-revocation audit evidence, rather than treating earlier safety as sufficient. This experiment tests whether that requirement can be implemented **without losing utility** or allowing unsafe resumption. The action choice remains hegemonic and deterministic: ACT only when the current risk gate is satisfied and policy suspension has ended; otherwise HOLD.

## Experimental design

Three paired policies:

- **stale** — historic last-five-audit confidence gate plus one currently quiet audit and a quiet sensor for release after suspension. This is the comparator, **not** evidence of valid independent reauthorization.
- **fresh3** — reset accumulated evidence on each sensor alarm, then require at least three fresh audit batches with a one-sided 95% Clopper–Pearson upper bound ≤2%, last two audits each ≤2 errors, and current sensor <1.5.
- **fresh5** — same rule, but at least five fresh batches.

Sensor alarm requires both sensor proxy ≥2.5 and at least three current audit errors. All policies share the same independent synthetic Bernoulli observations within each paired seed. Hidden risk regimes and recovery dates are visible only to the evaluator, never to the controller.

Three synthetic regimes: abrupt hazard/recovery, repeating hazard/recovery, and deceptive sensor-only shift. Each case runs 100 ticks with 140 audit roots and 150 held-out action outcomes per tick. Separate development seeds **100001–100040** and untouched evaluation seeds **100201–100280**, for 80 holdout seeds per regime.

## Policy-selection gate

Development candidate eligibility requires at most the stale policy's unsafe authorizations, and at most 110% of the stale policy's safe holds. Among eligible candidates select minimum development cost. **Neither fresh candidate qualified during development**, so `chosen_policy` is null, and no new controller was selected.

The new evaluation results are recorded as diagnostic comparisons only, not used for retroactive selection.

## New holdout results

| Metric | Stale | Fresh3 | Fresh5 |
|---|---:|---:|---:|
| Unsafe authorized ticks | 4 | 4 | 4 |
| Safe ticks withheld | **1,315** | 2,559 | 2,572 |
| Mean recovery delay (ticks) | **2.677** | 6.204 | 6.210 |
| ACT/HOLD changes | 764 | 749 | 749 |
| Authorized ticks | 17,649 | 16,405 | 16,392 |
| Wrong authorized outcomes | 8,003 | 7,414 | 7,409 |
| Illustrative total cost | **166,062.5** | 169,502.5 | 169,550.0 |

Cost = 10 × wrong authorized outcomes + 0.05 × withheld actions + 0.01 × audit labels + 0.2 × sensor observation per tick. The lower wrong-outcome count of fresh policies is mainly the result of withholding more actions, not proof of better conditional correctness.

**Acceptance gate:** no additional unsafe authorization, no more than 5% extra safe holds, nonincreasing total cost, and no longer mean recovery delay than stale. Both fresh policies fail three of four criteria.

**Conclusion:** Preserve the failed evidence and keep the previously accepted governing policy. A fresh certificate was not demonstrated economically competitive in these conditions.

## Reproduction

```bash
python aether/100/experiment.py
```

Requires NumPy and SciPy; generates `development_options.csv`, `seed_results.csv`, `trace_samples.csv`, `results.csv`, `manifest.json`. All values are synthetic. A fixed-time Clopper–Pearson bound on past observations is not an anytime or future-safety guarantee; hidden dependence and real-world failure modes are not tested.

## Next bound: AETHER-100B

Conditionally accumulate fresh evidence **only while a suspension is actually relevant to action**, avoid repeatedly resetting the recovery window during continuing hazards, and use independent development/holdout seeds again. Any shorter certificate must independently justify its uncertainty and safety. **Keep the phase at 50% until accepted.**

[Interactive Pages-ready report](https://davidwise01.github.io/oasis/aether/100/) · [Phase progress](../PHASE-II-STATUS.md) · [Previous 099B](../099b/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
