# SHEET 241 — Overlapping Local Failures & Fault Ledger

**Executed:** `python gate241.py` 21/21 PASS. Original S176 Node writer intentionally stops after its durable prepare. Target and floor are distinct child processes each holding uncommitted SQLite writes when both receive SIGKILL; both independently roll back. A dual-Ed25519-signed repair claim is rejected by the broker because no WAL commit exists. Binding and floor remain at genesis, writer retries stay quarantined, and the WAL remains byte-identical. Five hash-linked audit events are checked.

**Regression:** `python gate240.py` passes 14/14 orchestrator assertions and 53 inherited branch assertions (67 total) in separate child runs. Across the new gate and regression: **88/88 assertions passed**, but not in one simultaneous system.

**Full exact-tested executable archive:** `SHEET241-overlapping-fault-ledger.zip` (77,275 bytes, 53 files), SHA256 `873b785a93c737e6178c6041017aaced5a06f03a067bea62f51652441c66cda4`. Contains `gate241.py`, original S176 Node source and S240/S239/S238 gates. Executable source is in the conversation ZIP, not in this GitHub release-record commit.

**Limitations:** Integrated overlap is for prepare-only quarantine, not committed-orphan recovery during simultaneous failures. Test process kill is not hardware power loss. No real network partition or remote independent deployment. Progress remains **90% = 9/10 locally demonstrated engineering milestones**, not production-readiness.

Next S242: overlapped target/floor/broker failures for an actually committed but unbound WAL, with lost acknowledgments and deterministic restart recovery.