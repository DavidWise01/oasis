# SHEET 229 — Benchmark and Kernel Alignment

Current executable baseline: SHEET 228.

**Fresh test run:** five independent runs of `python gate228.py`; all 18/18 PASS, 90/90 repeated assertions. Times (seconds): 0.7023, 0.6635, 0.7226, 0.7054, 0.7000. Median 0.7023 s; mean 0.6988 s; range 0.6635–0.7226 s. This is suite wall time, not sustained TPS.

**Archive verification:** SHEET228-cryptographic-recovery-broker.zip 129137 bytes, 5 top-level members (contains nested S227 predecessor ZIP); zip.testzip() passed. SHA-256 1227dfc4122b3eec69f2106b65e10d7dba17ed632fce5a56bbbda650bcf195da.

## Ranked tested capabilities
1. Ed25519 target + floor evidence verification for exact repair state (S228).
2. SQLite-serialized conflicting repair updates: 1 accepted of 10 (S228).
3. WAL hash-chain and prepare/commit pair verification (S228).
4. Monotonic repair floor and replay denial (S228).
5. Live mTLS target/floor and durable ACK (S215–S222, historical; not rerun this benchmark).
6. Crash-quarantined WAL and signed repair (S210–S226, historical).
7. Separate writer/repair UIDs and read-only WAL to repair UID (S225–S226).
8. Ed25519-authenticated input provenance and reproducible target results (S217–S220).
9. SO_PEERCRED role checks (S227; focused S228 bypasses network by calling broker.run).
10. SQLite audit rows (S228) without external tamper-evidence.

## Release blockers
P0: Broker DB not exclusive to trusted broker UID; bypass remains possible.
P0: S227's inherited writer **bind** accepts a caller-proposed WAL head without independently validating the WAL. S228 hardens the *repair* path only.
P0: S228 focused gate uses local signing keys and does not rerun end-to-end independent mTLS recovery.
P1: S228 WAL verifier does not recompute prepareHash from input/result semantics, only compares prepare/commit references.
P1: WAL/SQLite not atomic; no cross-host partition or physical power-loss proof.

**Next:** enforce broker-exclusive DAC on control DB and validate WAL on both bind and repair; integrate separately signed mTLS target/floor evidence and rerun dedicated-UID crash flow.

The full local report is in the conversation attachment.