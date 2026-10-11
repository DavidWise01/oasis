# SHEET 235 — SQLite Repair Commit Crash Matrix (Partial Milestone)

New `gate235.py` local 15/15 PASS: real `os._exit` in forked broker process just before and after SQLite COMMIT. Before COMMIT, floor and binding rollback; signed retry accepted once. After COMMIT, both persist and replay is denied. In both cases SQLite integrity is `ok`, one repair audit row remains and original WAL is unchanged. The test uses genuine Ed25519 target/floor signatures and cryptographically verified broker logic over a prepared hash-linked WAL.

**Scope:** This checks one SQLite transaction boundary, not independent target/floor/WAL service crashes or hardware power loss. Full end-to-end cross-store atomicity remains unproven. Thus the local milestone checklist remains **90% (9/10)**, not production-readiness.

Full `gate235.py`, S234 predecessor source and runnable ZIP distributed in conversation. Next: fault-inject the original writer, target, floor, and broker under independent process termination and network-loss scenarios.
