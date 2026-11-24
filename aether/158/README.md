# AETHER-158 — Drift and alarm acceptance thresholds

**Phase X Turn 6/8 · 75% synthetic setup readiness · 0% empirical physical qualification.**

The *locally executed* `local_audit.py` tested 25 seeds × eight scenarios × 20 ticks, totaling **200 episodes and 4,000 decisions per policy**. **3,200/3,200 checks passed**: deterministic replay, evidence-chain integrity, tick order, exactly one decision per tick, no unsafe guarded dry-run ACT, operational HOLD, preservation of clean/rotation decisions and lack of hidden scenario labels in the policy function.

The signed-only comparator admitted **1,200 unsafe dry-run ACT** in six constructed fault windows. The drift/alarm-gated controller admitted **zero unsafe dry-run ACT** and preserved **2,800 safe dry-run ACT** (500 clean, 500 legitimate rotation).

Modeled gates include maximum per-tick drift budget .001, reference uncertainty .0005, modeled alarm detection agreement, 50 ms maximum alarm latency, a current calibration/baseline epoch and a conservative permission limit .025. Those numbers are *simulation contract parameters*, not physically measured tolerances. Fault cases: slow drift, abrupt drift, suppressed alarm, delayed alarm, stale drift record and baseline epoch forgery.

The [physical alarm register](physical_alarm_register.json) retains null actual sample and reference entries. **No hardware drift, real alarm latency, false-alarm rate or calibrated physical reference was measured. All real operational permissions HOLD.**

Locally executed source SHA-256: `f6ded480f5de2b82e1ed7e2ceb352016d7f63ab540183a53b9e6cdf5ae98de2e`. The GitHub `experiment.py` is a separately authored, fuller protocol implementation and has **not been executed from checkout**. The ZIP includes exact local source and 3,200 check rows. Pages deployment is not independently confirmed.

[Interactive HTML](index.html) · [GitHub implementation](experiment.py) · [Aggregate results](results.csv) · [Manifest](manifest.json) · [Physical alarm register](physical_alarm_register.json) · [Phase X status](../PHASE-X-STATUS.md).
