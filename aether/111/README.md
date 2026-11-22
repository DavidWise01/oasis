# AETHER-111 — Unseen Dynamics and Resource Stress

**Phase IV, Turn 7 of 8: FAILED. Progress remains 6/8 = 75%.**

Frozen AETHER-110 controller (no retraining, threshold selection or retuning) evaluated under five unfamiliar synthetic conditions. The test script imports the original `../110/experiment.py` unchanged. New evaluation seeds: **111101–111180**, paired across both controllers. **400 episodes/controller × 24 decisions = 9,600 decisions per policy.**

## Scenarios and explicit limits

1. **Price shock:** evidence tariff rises sixfold in realized cost, without informing the frozen scheduler.
2. **Sensor dropout:** sensor downtime is returned as *560 zero-filled samples*, demonstrating an unsafe evidence-input convention.
3. **Hidden correlation:** 56 independent Bernoulli draws copied tenfold to appear as 560 reports, with ancestry hidden from the controller.
4. **Abrupt spike:** unexpected risk increases from 0.3% to 11%.
5. **Moving oscillation:** rapidly changing risk of 0.3% or 5.7%.

Truth labels and generation mechanisms are evaluation-only. All policies receive paired observations and held-out action outcomes.

## Results

| Environment | Cost savings adaptive vs fixed | Additional unsafe ticks |
|---|---:|---:|
| Price shock | +645.4 | 0 |
| Sensor dropout | +1,558.7 | 0 |
| Hidden correlation | +279.4 | **+45** |
| Abrupt spike | +3,259.9 | 0 |
| Moving oscillation | +3,853.0 | 0 |
| **All** | **+9,596.4** | **+45** |

Total fixed **149,615** units; adaptive **140,018.6** units. Independent sample reports purchased: fixed 4,400,000; adaptive 3,591,060. Authorized actions: fixed 4,706; adaptive 6,184. Wrong authorized outcomes: fixed 2,491; adaptive 3,533. Unsafe authorization ticks: fixed 48; adaptive 93.

**Acceptance:** no cost regressions AND no additional unsafe authorizations in EACH unseen environment. Costs passed; hidden correlation failed. **Do not promote.**

## Deterministic checks

The experiment performs 800 same-input hash replay tests and 800 future-perturbation prefix tests. All pass. They establish deterministic, causal processing, but cannot establish the validity of upstream evidence.

## Reproduce

Run `python aether/111/experiment.py` from a checkout containing `aether/110/experiment.py` (NumPy and SciPy). Generates `results.csv`, `comparisons.csv`, `seed_results.csv`, `trace_samples.csv`, and `manifest.json`.

## Honest limitations and next design

**Critical:** Missing data represented as zeros can be mistaken for clean sensor observations. Duplicate reports without source lineage can be mistaken for independent samples. The correct fix requires an explicit input contract with `available`, `valid`, and `root_count` fields rather than merely adjusting thresholds. Reliable hidden-root deduplication is not possible without provenance metadata or validated conservative assumptions.

The next iteration is **AETHER-111B: Fail-Closed Evidence Packet Contract**. Retain the single hegemonic controller; enforce invalid/missing/unknown-ancestry -> HOLD; retest the same five stress regimes on new evaluation seeds. Do not add quorum or Byzantine consensus within this phase. Continue to report the true actual completion percentage until the gate is passed.

[Visual GitHub Pages report](https://davidwise01.github.io/oasis/aether/111/) · [Phase IV tracker](../PHASE-IV-STATUS.md) · [Frozen reference](../110/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
