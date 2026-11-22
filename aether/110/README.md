# AETHER-110 — Deterministic Resource Scheduling

**Phase IV, Turn 6 of 8: ACCEPTED · 75% complete (synthetic gate).**

## Invariant 110

Only acquire additional independent observations when their possible outcomes can change the present decision. A single deterministic controller issues **ACT** only after a risk certificate, otherwise **HOLD**. Previous decisions and evidence cannot be overwritten.

## Executed synthetic experiment

- Five environments: stable safe, hazard burst, oscillating risk, scarce observation budget, tenfold copied reports.
- Paired observation/outcome seeds: development **110001–110030**, untouched evaluation **110101–110180**.
- 24 inspections per episode; up to 560 independent Bernoulli roots and 150 held-out action outcomes per inspection.
- Candidate episode budgets 7,000 / 9,000 / 11,000 independent roots, selected using development data alone. **Selected budget = 11,000**.
- One-sided binomial upper bound with Bonferroni confidence allocation `alpha = 0.05 / (24 × 4)`. Four planned looks per inspection with up to 140 fresh roots per look.
- The adaptive scheduler stops when a bound ≤0.025 certifies ACT, or when an *optimistic completion with zero remaining errors* would still fail to certify. If the budget is insufficient, HOLD.
- The fixed comparator purchases up to 560 roots every inspection until budget exhaustion. Copied reports count as 56 distinct roots per inspection, **not** 560.
- Both controllers use identical seeded observations and outcome draws, never true hidden risk when deciding.

## Independent holdout results

| Metric | Fixed | Adaptive |
|---|---:|---:|
| Decisions | 9,600 | 9,600 |
| ACT | 3,839 | 5,036 |
| HOLD | 5,761 | 4,564 |
| Independent roots | 3,627,520 | **2,976,660** |
| Incorrect authorized outcomes | **1,701** | 2,243 |
| Unsafe authorized ticks (simulator true risk >2.5%) | **0** | **0** |
| Total illustrative cost | 96,492.7 | **86,426.6** |

Saving: **650,860 roots (17.94%)**, **10,066.1 cost units (10.43%)**.

Individual environment costs all declined or matched: stable 18,620→17,631.6; burst 21,012.5→17,894; oscillation 20,940→17,584.4; scarcity 20,445→17,841.4; duplication 15,475.2→15,475.2.

**Important:** More ACT activity caused 542 more incorrect action outcomes. The gain relies on the stated utility weights: 10/wrong authorized outcome, 7.5/HOLD inspection, 0.01/independent root. The experiment does not show universal decision accuracy improvement or production safety.

## Acceptance and reproduction

All predeclared held-out gates passed: total cost not higher, unsafe authorizations not higher, ACT opportunities not fewer, deterministic replay hashes equal.

Run `python aether/110/experiment.py` with **NumPy and SciPy**. It regenerates `development_options.csv`, `results.csv`, `seed_results.csv`, `trace_samples.csv`, `manifest.json`. The portable checked-in source uses the same seed generation, policies and comparison criteria as the executed local source.

Synthetic model limitations: samples are independent except when explicitly copied tenfold; historical binomial coverage assumes those declared roots. We did not test adversarial forged root metadata, arbitrary drift, hardware sensors or production reliability.

[Pages-ready interactive lab](https://davidwise01.github.io/oasis/aether/110/) · [Phase IV progress](../PHASE-IV-STATUS.md) · [Predecessor](../109b/)

## Next — AETHER-111: Unseen Dynamics and Resource Stress

Test the frozen scheduler against unexpected correlation, drifting costs, repeated outages and nonstationary risks. The phase earns 87.5% only if the stress acceptance gate passes. Closure remains AETHER-112.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
