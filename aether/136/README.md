# AETHER-136 — Phase VII integration and empirical assurance gap freeze

**Accepted local synthetic closure:** 25 new seeds × eight simulated physical-instrument faults × 32 ticks = **200 episodes**, **6,400 action decisions**, **1,600/1,600 deterministic checks**. Under the frozen local AETHER-135B reference-bound gate: **0 unsafe ACT**, **2,200 safe ACT**, **3,000 safe HOLD**, and **3,200 simulated reference acquisitions**.

Clean and valid-replacement scenarios preserved **800/800 safe ACT each**. Fault cases without trustworthy external-reference packets fail closed to HOLD. Those cases provide no evidence of a corrected physical measurement; they simply do not authorize ACT.

**Ten previous Phase VII experimental versions** are inventoried in `archive_inventory.csv` with SHA-256 hashes of local source and manifests. The failed **AETHER-130, AETHER-133 and AETHER-135** are preserved without being counted as accepted turns.

**Unresolved physical gap:** The source of the calibrated reference reading is simulated. Its physical independence, calibration uncertainty, acquisition path, device root and correctness are **assumed**. Digital signing and replay tests cannot demonstrate these facts. No physical instrument was connected. Zero unsafe ACT is an outcome of 6,400 constructed software decisions, **not** a physical or probabilistic assurance for real instrumentation.

**Reproducibility:** Local frozen AETHER-135B source SHA-256 `e50d627d9231d9032027a4e5ffa3a4f307dd64d2d8d63dfcc9947ffe191dcf16`. GitHub `experiment.py` is a **separately authored repository-compatible harness**; its complete checkout execution has not been independently verified, and the published results/manifest represent the local executed program. The complete local run with checks and traces is distributed as the downloadable ZIP linked in the conversation.

**Phase VII = 8/8 = 100% of constrained synthetic acceptance**, not physical qualification. No quorum or Byzantine-voting procedure introduced. Phase VII is frozen; a future independent physical-validation program would begin at 0%.

[Reproduction script](experiment.py) · [Aggregate results](results.csv) · [Local evidence manifest](manifest.json) · [Local source inventory](archive_inventory.csv) · [Interactive laboratory](index.html).
