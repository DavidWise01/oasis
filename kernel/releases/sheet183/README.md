# SHEET 183 — Atomic Coordinator Intent & Durable History Gate

**Verified locally:** S183 22/22 PASS; inherited S182 22/22 PASS; inherited S181 19/19 PASS. Focused checks across these three releases: **63/63**.

The executable implementation and test gate are provided in `SHEET183-atomic-coordinator-gate.zip` (11,034 bytes), SHA-256 `4f374db7697226a9f243668754576529398d84204ccaab4a73355335a9982741`.

S183 uses SQLite `BEGIN IMMEDIATE` to atomically acquire one coordinator intent with owner/epoch and a hash-linked event record, disallows a second pending operation, reconciles a committed target by durable request ID, checks signature-backed target heads, and blocks stale owners and tampered history. It recovers pending state across database reopen.

**Boundary:** this is a new SQLite bridge, **not** the original S176/S177 Node.js WAL integration. Signing remains a separate step. Tests use one host, no independent external authority, no mTLS, and no hard power-loss test. The full historical regression chain was not rerun. The source and gate are in the complete ZIP; this commit publishes the release record only.

Next SHEET 184: reconcile the original S176 WAL bytes against SQLite intents and separately signed anchors, run hard-kill tests at each state transition, and publish a self-contained source tree.
