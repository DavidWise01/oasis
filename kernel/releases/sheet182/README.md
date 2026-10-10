# SHEET 182 — Hard-Exit Recovery and Atomic Fencing

**Executed locally:** new SHEET 182 22/22 PASS and inherited SHEET 181 19/19 PASS. Three child processes exited immediately with `os._exit(137)` after respectively (a) durable prepare, (b) SQLite commit, (c) signed head persistence. Recovery quarantines uncertain state and reports signed-head pending cleanup correctly.

Eight concurrent SQLite target appenders attempted cursor index 1: one committed, seven rejected. Stale epoch was rejected, new owner sequential write accepted, final target hash chain verified.

**Complete tested executable ZIP:** `SHEET182-hard-exit-fencing-gate.zip`, 8,244 bytes, SHA-256 `67a058b86685de709ba6f15f352430faa5a3bd2af108d711e2671bccd0a8e4db`, attached to the original conversation. ZIP includes `gate182.py`, `worker182.py`, S181/S180/S179 predecessor source, regression gate and README. This GitHub change only publishes its release record.

**Boundary:** S176/S177 Node.js WAL is not wired into this test; the S181 coordinator's file journal is not safe under concurrent writers, although S179 target SQLite append is atomic. Local processes only, no hard power loss, no independent remote anchor, no exactly-once distributed protocol. Fork-based concurrency test is POSIX specific.

Next SHEET 183: actual durable S176 WAL reconciliation adapter, atomic coordinator ownership claims, and isolated remote authority validation.