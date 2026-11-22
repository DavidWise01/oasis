# AETHER-109 — Recovery When Independent Sensing Resumes

**Phase IV, Turn 5 — FAILED GATE. Completion remains 4/8 = 50%.**

One deterministic decision authority, evidence available up to the current tick only, separate identifiers for fresh observation batches. Synthetic test, 100 disjoint seeds (109001–109100) in four regimes, 30 ticks each and two paired policies.

Outage: ticks 8–13, resumption tick 14 (zero-indexed simulation start=7, resume=13). The **stale_reuse** comparator resumes pre-outage authorization for three ticks, ignoring the current audit decision. The **fresh_certificate** controller begins a new two-batch (560 independent samples per tick) certificate after resumption and ignores delayed or duplicated reports.

| Scenario | Stale cost | Fresh cost | Unsafe stale → fresh |
|---|---:|---:|---:|
| Safe resume | 29,660 | 29,670 | 0 → 0 |
| Hazard at resume | 59,590 | 30,670 | 300 → 0 |
| Delayed delivery | 58,020 | 30,910 | 300 → 0 |
| Duplicate flood | 31,790 | 31,750 | 0 → 0 |
| **All** | **179,060** | **123,000** | **600 → 0** |

**Prespecified four-part gate:**
1. Reduce unsafe authorized inspections: PASS.
2. No total-cost regression in *any* scenario: **FAIL** (+10 safe-resume).
3. Safe-resume first useful action within 3 ticks: PASS (1 tick).
4. Retain 92% of safe-resume active opportunities: PASS.

**Decision: do not promote.** Overall cost is substantially lower but per-scenario nonregression is a hard requirement. The stale comparator is intentionally unsafe and should not be interpreted as a recommended production strategy.

A preliminary version of the local prototype added the same root batch twice to the recovery certificate. This was corrected before the final report; the committed `experiment.py` samples each batch only once. A certificate must use two actually distinct inspection batches.

**Limitations:** Bernoulli synthetic roots, fixed known outage boundary, fixed loss weights, no guarantee against correlated ancestry or real sensor failure. No witness/quorum/Byzantine mechanisms introduced.

**Reproduce:** `python aether/109/experiment.py` (NumPy/SciPy). Creates results.csv, seed_results.csv, trace_samples.csv and manifest.json.

**Next: AETHER-109B — cost-neutral fresh reauthorization**, using new evaluation seeds and a frozen acceptance gate; Phase IV continues at 50% until accepted.

[Interactive report](https://davidwise01.github.io/oasis/aether/109/) · [Phase IV progress](../PHASE-IV-STATUS.md) · [Previous 108](../108/)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
