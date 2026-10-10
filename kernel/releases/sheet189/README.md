# SHEET 189 — Hard-Kill WAL/SQLite Reconciliation

Tested locally: `python gate189.py` **15/15 PASS**, inherited `python gate188.py` **15/15 PASS**.

The test invokes the original S176 Node dispatcher while the SQLite coordinator holds `BEGIN IMMEDIATE`, observes durable WAL append, and kills the coordinator with real SIGKILL **before** SQLite binds the new head. After restart, the two extra WAL records are quarantined against the older SQLite binding and Ed25519-signed floor; stale owners, newly claimed epochs and forged floor signatures cannot authorize continuation. This is an intentionally unresolved orphan—not an automatically recovered transaction.

Full executable ZIP (includes `gate189.py`, `kill_worker189.py`, the original S176 runtime and S188 predecessor): `SHEET189-hardkill-signed-reconciliation.zip`, SHA-256 `fdff67637077e525bebb6250ed953eaf4eb2bd46afd23a4db9890c0882def85b`, 43,840 bytes.

**Limits:** Single host, local signed floor and SQLite target, no external durable anchor, not a cross-store atomic transaction, no physical power-loss testing. Repository files require the full source layout in the ZIP. Next SHEET 190: separate signed repair authority and strict request-ID cross-store reconciliation.
