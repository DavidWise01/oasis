# SHEET 187 — Recovery Owner Fencing and Signed Archive

Local executable gate `python gate187.py`: **24/24 PASS**. Six SQLite-competing process claims allocate distinct sequential owner epochs; signed Ed25519 archive verifies its monotonic cursor, generation and historical hash chain. A Node child is killed with an outstanding filesystem lock; it persists and is quarantined.

**Exact runnable package:** `SHEET187-fencing-signed-archive.zip`; SHA-256 `8e220913d7fed072fd0753181f8e2f0348ca2c94b0971a591282037513a0a9dd`, available in this conversation. Contents: `fence187.py`, `gate187.py`, `lock187.js`, `README-SHEET187.md`.

Boundaries: one host; no independent rollback anchor; original S176 WAL writer not yet fenced atomically by epochs; no cross-store atomicity or physically separate authority, full inherited regressions not rerun. This repository note is not itself the executable gate.

Next: SHEET 188 — reject stale epochs inside the original WAL write critical section with a trusted authoritative epoch service, then test races/crashes.
