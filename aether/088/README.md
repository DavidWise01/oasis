# AETHER-088 — Sequential Risk Certification and Evidence Independence

**Invariant 088:** Permission to act must remain statistically defensible even when the system repeatedly checks whether enough evidence exists.

This reproducible synthetic experiment evaluates **1,000 trials per condition**, with 40 prespecified looks, 30 new independent roots per look, and either one observation or six duplicate copies per root.

- Safe true conditional wrong-sign risk: 0.3%.
- Unsafe true conditional wrong-sign risk: 2.4%.
- Authorization risk budget: 2%.
- Statistical error allowance: alpha 5%.

Three policies:

1. **Naive:** exact one-sided binomial upper bound with alpha=0.05 at every inspection; erroneously considers six copies to be six independent samples in the duplicate scenario.
2. **Anytime / unique roots:** exact one-sided binomial upper bound using alpha/40 at each of 40 inspections, counting only unique independent roots.
3. **Fixed final / unique roots:** performs one test at 1,200 unique roots, alpha=0.05.

## False certification of unsafe risk

| Evidence | Naive repeated test | Anytime unique roots | Fixed final |
|---|---:|---:|---:|
| Independent roots | 5.8% | 0.2% | 0.3% |
| Six copies per root | **62.5%** | **0.1%** | 0.4% |

## Correct certification of genuinely safe risk

| Evidence | Naive repeated | Anytime unique | Fixed final |
|---|---:|---:|---:|
| Independent roots | 100% | 100% | 100% |
| Six copies per root | 100% | 99.8% | 100% |

**Guarantee and limits:** By Bonferroni, alpha/40 controls family-wise false certification probability across these 40 prespecified inspections **if unique source roots are independent and the common Bernoulli failure probability is stationary**. It does not prove risk control after distribution changes, unknown shared ancestry, adversarial optional choice of new tests, or arbitrary sequential dependence. The experiment is synthetic, not instrument validation.

Run `python aether/088/experiment.py` (requires numpy and scipy) to regenerate the results, look audit, and manifest. Public visual report: https://davidwise01.github.io/oasis/aether/088/

**Next bound — AETHER-089:** Online lineage-aware confidence sequences under evolving, nonstationary audit conditions. Track source roots, unequal evidence weights, and temporal drift instead of assuming all future independent roots share one constant risk.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
