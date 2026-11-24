# AETHER-144 — Phase VIII readiness integration and evidence freeze

**Synthetic software readiness: 8/8 = 100%** · **Empirical physical validation: 0% (NOT PERFORMED)**.

The locally executed final integration ran **25 fresh seeds across eight sensor-reference fault scenarios**, **200 episodes**, **4,800 decisions**, and **1,600/1,600 deterministic checks**. The frozen local AETHER-143 policy achieved **zero unsafe dry-run ACT**, **3,600 safe dry-run ACT**, and **zero operational ACT**. Both clean and valid-rotation cases preserved **600/600** safe dry-run actions.

All seven previous Phase VIII local evidence ZIPs were inventoried. The source and manifest SHA-256 hashes are published in `archive_inventory.csv`; the historical experiments were *inventoried*, not exhaustively rerun. No prior source was modified.

**Explicit unresolved gap**: the external bench in AETHER-143 is a simulated truth oracle. Keys are software HMAC secrets. No instrument was physically challenged, no reference standard verified, no measured uncertainty/coverage demonstrated, no same-path acquisition hardware proved, and no drift alarm tested empirically. Synthetic completion cannot change these facts. **Every real-world physical permission remains HOLD.**

**Reproducibility limitation:** `results.csv` and `manifest.json` were produced by locally executed source archived in the companion evidence ZIP; GitHub `experiment.py` is a separately authored repository-checkout harness. Its independent numerical replay remains unverified. Live GitHub Pages deployment is unverified.

[Executable GitHub checkout harness](experiment.py) · [Local results](results.csv) · [Manifest](manifest.json) · [Seven-bound source inventory](archive_inventory.csv) · [Interactive HTML lab](index.html).

Next phase: independently sourced physical qualification protocol, starting at zero evidence, without introducing quorum/Byzantine governance.
