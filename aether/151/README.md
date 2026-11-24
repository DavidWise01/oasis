# AETHER-151 — Blind Adversarial Data Intake Rehearsal

**Phase IX 7/8 · synthetic software protocol readiness 87.5% · independently qualified physical evidence 0%.**

An independently authored local Python audit of **30 seeds × eight scenarios × 20 ticks** ran **240 episodes per policy**, **4,800 decisions per policy**, and **3,840/3,840 deterministic checks**. The signed-only policy authorized **1,440 unsafe dry-run ACT** in six constructed fault windows. The blind evidence-intake gate authorized **zero unsafe dry-run ACT** while preserving **3,360 safe dry-run ACT**, including **600/600 clean** and **600/600 legitimate-rotation** actions. All operational actions HOLD.

**Blindness:** `decide(submission)` receives only signed acquisition data, separate reference/bench receipts and raw bytes. It does not receive the scenario, seed, fault label or hidden synthetic truth. Scoring occurs after decisions, on the test side. That is a limited software property, not verified blindness to real physical confounders.

Fault conditions: missing raw acquisition, replayed reference counter, substituted ingress route, self-issued reference root, signed reference contradicting bench receipt, and bench challenge nonce mismatch. The controller checks binding, hash, issued root, measurement disagreement and conservative uncertainty.

**Limitations:** The nominally independent bench is a software oracle reading synthetic ground truth. The signing roots are mock HMAC secrets. A compromised real reference or common-origin failure could defeat these checks. No physical laboratory, traceable calibration, instrument, same-path probe or uncertainty coverage was qualified. Real operational action authority remains **HOLD**.

**Provenance:** `results.csv`, `manifest.json`, and the companion evidence ZIP record the locally executed audit, SHA-256 of `local_audit.py`: `d4861612d1858ed333da70843251c24e7d40f3d14eede303afd97079f3f165a7`. The separately published GitHub `experiment.py` is a more extensive checkout-oriented experiment, not the same bytes; GitHub checkout execution has **not yet been verified**. The ZIP includes the complete local source, all checks, seed results, manifest, and hash-chained samples. GitHub Pages deployment status is unverified.

[Github executable](experiment.py) · [Local results](results.csv) · [Local manifest](manifest.json) · [Interactive lab](index.html) · [Phase IX tracker](../PHASE-IX-STATUS.md).

**Next AETHER-152**: qualification evidence freeze of synthetic software readiness, with the physical validation gap explicitly OPEN.
