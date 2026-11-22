# AETHER-104 — Independent Evidence Root Deduplication

**Phase III, Turn 1/8: PASS · 12.5% phase completion.**

The AETHER Phase II controller remains closed at AETHER-103. Phase III is a separately scoped evidence ancestry study; source observations qualify evidence but do not acquire action-governing authority.

## Invariant 104

**Multiple messages copied from one source ancestor count as one root, not multiple independent corroborations.** A root can count only one uncontradicted value. A decision requires at least two distinct roots endorsing the selected value. Otherwise choose HOLD.

## Study

6,000 synthetic deterministic cases, 2,000 each across:
1. **Independent:** three ancestry roots with independent, 88%-accurate binary reports; A and B are each copied once, so message counts exceed root counts.
2. **Cloned corruption:** four copies of one deterministically wrong root compete with two different correct roots.
3. **Insufficient roots:** one root copied four times plus a second independent root; each root is 80%-accurate.

All report IDs, source ancestry labels, binary truth, selected actions and 12 example SHA-256 trace digests are reproducible from seeds 104000–105999. The simulator truth is used for measurement, never by the decision function.

## Results

| Scenario | Naive incorrect | Root-aware incorrect | Root-aware HOLD |
|---|---:|---:|---:|
| Independent | 79 | 79 | 0 |
| Cloned corrupted ancestor | 2,000 | 0 | 0 |
| Insufficient distinct roots | 393 | 74 | 618 |
| **All** | **2,472** | **153** | **618** |

The root-aware strategy makes fewer incorrect decisions in this constructed mixture, but chooses HOLD in 618 cases (10.3% of all cases). **Do not interpret 93.8% fewer wrong decisions as a general effectiveness guarantee**; the cloned-corrupt scenario is deliberately structured to demonstrate source duplication.

### Prespecified acceptance gate
- Root-aware policy no worse in total wrong decisions: **PASS**.
- At least 90% fewer wrong decisions in cloned-corrupt cases: **PASS**.
- Never authorize from fewer than two ancestral roots: **PASS**.

## Reproduction

`python aether/104/experiment.py` — Python standard library only. Generates `results.csv`, `seed_results.csv`, `trace_samples.csv`, `manifest.json`. Compare the generated CSV with committed `results.csv`.

## Limitations and next bound

The source ancestry labels are supplied correctly as part of the toy experiment. An attacker can claim a forged or fresh root ID, or several apparent roots can share one upstream ancestor. Those cases are **not protected here**.

**Next: AETHER-105 — Forged Root IDs and Shared Upstream Lineage**, with a separate validation gate and preserved counterexamples.

[Phase III charter](../PHASE-III-104-111.md) · [Live tracker](../PHASE-III-STATUS.md) · [Interactive report](https://davidwise01.github.io/oasis/aether/104/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
