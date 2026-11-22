# AETHER-094 — Generalization Confidence and Regret

**Invariant 094:** A learned policy earns permission to replace its baseline only when independent evidence supports a dependable improvement—not merely a favorable average.

## Experiment

AETHER-093's selected state policy is frozen before evaluation: **quiet → no sentinel; uncertain → sentinel; denied → no sentinel**.

AETHER-094 uses 40 paired evaluation seeds (94101–94140), 72 ticks per seed in each of six environments (stable, step, ramp, burst, asymmetric burst, oscillatory shift), and four competing policies (rolling-only, periodic, continuous, frozen learned). Each policy sees the same audit, sentinel and decision-test outcomes in its seed/regime. No held-out outcome is used to select the learned policy.

Each tick contains 140 audit labels, 150 independent action outcomes, and optionally 80 sentinel labels. Cost is 10 per wrong action, 0.05 per withheld action, and 0.01 per label. A fixed-time Clopper–Pearson bound is applied to recent audits; it is not guaranteed to protect instantaneous risk under change.

## Held-out results

| Policy | Cost | Wrong actions | Sentinel probes | Unsafe-authorized ticks |
| --- | ---: | ---: | ---: | ---: |
| Rolling-only | 123,912.0 | 6,831 | 0 | 161 |
| Periodic | 126,027.0 | 6,708 | 3,600 | 135 |
| Continuous | 134,118.5 | 6,248 | 17,280 | 72 |
| Learned | 123,795.9 | 6,459 | 3,258 | 96 |

The learned policy saves **116.1 cost units, or 0.094%**, versus rolling-only. But its savings across 40 paired seeds average **+2.903 units per seed**, with a percentile bootstrap interval of **[−14.200, +21.788]** using 10,000 bootstrap draws. The interval includes zero.

The learned policy wins in step, burst, and oscillatory regimes but loses in stable, ramp and asymmetric-burst regimes. Under three of five cost perturbations, rolling-only wins instead: wrong-action penalty 3, label cost 0.05, or abstention cost 0.15.

## Promotion decision: **REJECT / RETAIN BASELINE**

Promotion requires both:
1. Positive lower bound on paired-seed bootstrap improvement.
2. No evaluated regime with positive regret versus rolling-only.

**Neither requirement passes.** The learned policy remains experimental; retain rolling-only as operational baseline within the simulator.

## Reproduction and limitations

Run `python aether/094/experiment.py` with NumPy and SciPy. It regenerates `results.csv`, `seed_results.csv`, `paired_seed_benefits.csv`, `cost_sensitivity.csv` and `manifest.json`. Historical source and outputs are append-only in this version directory.

The confidence interval reflects uncertainty from 40 synthetic paired seed draws—not a universal, distribution-free, anytime-valid or real-world performance guarantee. Bootstrap comparisons do not guarantee safety after novel environmental changes. Additional external datasets, seed families, cost modeling and risk controls are needed.

[Interactive GitHub Pages report](https://davidwise01.github.io/oasis/aether/094/) · [Previous AETHER-093](../093/)

## Next natural bound — AETHER-095: Evidence-Efficient Conditional Promotion

Instead of choosing between all-or-nothing deployment and permanent rejection, ask whether specific measured environmental states can support **conditional, reversible promotion**. Use separated discovery, selection and certification data, impose a per-regime regret budget, and require fallback when confidence decays.

**Invariant 095 candidate:** Permission to adapt is local to the evidence supporting it, reversible when that evidence fails, and never inherited from aggregate performance.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
