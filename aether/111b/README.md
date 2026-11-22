# AETHER-111B — Fail-Closed Evidence Packet Contract

**Phase IV / Turn 7 of 8 — Accepted on synthetic holdout; 87.5%.**

This preserves the original **failed AETHER-111** source and results rather than overwriting them.

## Boundary and design

One controller remains authoritative. Each observation packet declares `status` (valid / missing / unverified), `reported_count`, `certified_unique_count`, and observed Bernoulli values. A packet with invalid status, mismatched counts, or uncertain independence must not produce an ACT decision. This is a **trusted ingress contract**, **not** a cryptographic proof of genuine independence. A forged packet could defeat it; that case is not addressed here.

The fixed comparator and adaptive controller use the *same* explicit packet contract. Both apply a 2.5% risk gate with a 5% confidence budget adjusted for 24 inspection ticks and four preannounced acquisition looks. Adaptive buys up to 4 chunks of 140 independent readings per valid packet and may stop early when a certificate is granted or mathematically impossible at the remaining budget. Budget = 11,000 roots per episode. Actions are ACT or HOLD.

## Independent synthetic evaluation

- Five scenarios: price shock, declared dropout, unverified tenfold correlation, abrupt spike, moving oscillation.
- Diagnostic/development seeds 111201–111220 reserved; evaluation **111301–111380** per scenario.
- 80 episodes per scenario × 5 scenarios × 2 policies = 800 policy episodes, **19,200 decision opportunities**.
- Replay equality, future-prefix causality, resource-budget accounting and packet-validity checks are recorded in `checks.csv` (800 lines).
- **Both corrected policies** issued no unsafe authorized ticks on these synthetic seeds; this does not establish zero real-world risk.

| Scenario | Adaptive cost savings | Additional unsafe authorizations |
|---|---:|---:|
| Changing observation prices | 83.7 | 0 |
| Explicit sensor dropout | 1,064.4 | 0 |
| Unverified correlation | 0 | 0 |
| Abrupt hazard | 2,965.5 | 0 |
| Moving oscillation | 3,890.7 | 0 |
| **All** | **8,004.3** | **0** |

| Total | Fixed | Adaptive |
|---|---:|---:|
| ACT | 3,441 | 4,132 |
| HOLD | 6,159 | 5,468 |
| Independent samples bought | 3,222,400 | 2,568,320 |
| Invalid/unverified packet HOLD ticks | 2,800 | 2,800 |
| Wrong authorized action outcomes | **1,657** | **2,079** |
| Total illustrative cost | 138,986.5 | **130,982.2** |

The adaptive policy incurs more wrong outcomes because it acts more often. The aggregate cost falls under the chosen cost function: 10 per wrong authorized outcome, 7.5 per HOLD inspection and 0.01 per independent observation (sixfold tariff for the price-shock scenario).

## Reproduce

```bash
python aether/111b/experiment.py
```

Requires NumPy and SciPy. Regenerates `results.csv`, `comparisons.csv`, `checks.csv`, `seed_results.csv`, `trace_samples.csv` and `manifest.json`.

The unchanged failed stress test remains [AETHER-111](../111/). For practical deployment, independently establishing the trustworthiness of packet status is an unsolved external requirement; no distributed quorum, Byzantine consensus or witness architecture is part of this phase.

**Acceptance:** all five scenarios passed no added unsafe authorizations and no realized-cost regression. Phase IV may advance to **87.5%**. Next: **AETHER-112 — Integration, reproducibility and phase freeze.**

[Interactive Pages-ready lab](https://davidwise01.github.io/oasis/aether/111b/) · [Phase IV live status](../PHASE-IV-STATUS.md)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
