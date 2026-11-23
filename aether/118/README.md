# AETHER-118 — Risk-Audit Freshness Under Interrupted Acquisition

**Phase V / Turn 6 of 8: synthetic acceptance PASSED; phase 75% complete.**

## Governing invariant

A fresh clock does **not** grant action authority. A risk-audit packet must have an authenticated signature, expected source and epoch, genuine independence certification, current observation tick, matching protected acquisition counter, monotonically increasing packet sequence, and unexpired one-tick validity. A packet that fails any required field cannot authorize an action. One deterministic controller returns exactly one of **ACT** and **HOLD**.

## Executed evaluation

- 50 new seeds per scenario (118001–118050); eight scenarios; 36 ticks per case; 14,400 inspections per policy.
- Scenarios: clean, 3-tick delivery delay, missing packets, replayed older packets, mismatched acquisition counter, stale but correctly signed packets, duplicated sequence IDs, and recovery after a five-tick outage.
- Synthetic Bernoulli audit: 560 observations/packet, 0.3% safe risk, 7.5% true hazard during ticks 12–20.
- Compared an 8-tick cached-packet policy with strict same-tick validation, under matched observations and costs.
- Each case has five deterministic checks: replay, append-only chain, exactly one action, fail-closed on unaccepted packets, accepted packet sequence equals current tick.

## Holdout results

| Policy | Unsafe authorized ticks | Safe ACT | Safe HOLD | Total illustrative cost |
|---|---:|---:|---:|---:|
| Cached risk | 1,600 | 10,796 | 4 | 985,364.8 |
| **Strict current risk** | **0** | **10,796** | **4** | **358,164.8** |

Cost difference: 627,200 units in this constructed test. The cost model is 10 × expected wrong outcomes for ACT, 0.05 × withheld outcomes for HOLD, and 0.01 per label for each delivered packet. The expected-cost result is a simulation consequence, not real-world monetization.

**All five acceptance gates PASSED.** All 4,000 deterministic checks passed. The strict verifier kept clean availability at 1,350 of 1,350 safe actions.

## Reproduce

Requires Python 3, NumPy and SciPy.

```bash
python aether/118/experiment.py
```

This generates `results.csv`, `checks.csv`, `seed_results.csv`, `trace_samples.csv` and `manifest.json`. The repository contains verified source and results; trace_samples.csv is generated from source and available in the local downloadable outputs rather than checked in after an incomplete transport was detected.

## Scientific limits

The simulation supplies correct and trusted HMAC acquisition signatures, independently generated audit observations and a tamper-resistant current counter. A forged measurement signed by an authorized yet compromised signer cannot be distinguished here. All test scenarios have known risk change points, though the controller never reads the true risk at decision time. The Clopper–Pearson bound is fixed-time and does not by itself prove safety under arbitrary drift or optional stopping. Repeated check results are deterministic integrity tests, not separate corroborating sources. No witness quorum or Byzantine protocol is introduced.

[Interactive lab](https://davidwise01.github.io/oasis/aether/118/) · [Phase V tracker](../PHASE-V-STATUS.md) · [AETHER-117B](../117b/)

**Next natural bound — AETHER-119: Packet-Loss Recovery With Bounded Availability.** Separate detection of evidence loss from safe resumption; test delayed reauthorization and high interruption rates.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
