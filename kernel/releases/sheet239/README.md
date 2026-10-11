# SHEET 239 — Mid-Prepare Crash Quarantine

**Tested locally:** `python gate239.py` **17/17 PASS**, running original S176 Node `worker186.js` with its `after-prepare` fault. One fsync-written prepare without commit is preserved. Subsequent append attempts fail `PENDING_RECONCILIATION`. The S234-derived broker rejects an attempted repair of that uncommitted WAL even when target and floor statements carry valid locally generated Ed25519 signatures; SQLite bound head, floor generation and repair audit remain unchanged. Three more retry attempts remain quarantined; WAL bytes do not change.

**Exact runnable release:** `SHEET239-mid-prepare-quarantine.zip` (73,911 bytes, 52 files), SHA-256 `1482cf6e3eb7ad1755292bd4b8497eb017ce36cab528f775268eeed96ede0fab`; includes `gate239.py`, the full original Node writer under `s176/`, S238 process gates and all Python dependencies. ZIP archive integrity verified.

**Progress: 90% (9/10 local milestones)**. Not a production-readiness percentage.

**Boundaries:** Uses original writer's injected after-prepare exception rather than arbitrary `SIGKILL`; locally generated signed statements; no coordinated target/floor crashes in this new gate. No automatic commit/rollback of prepare-only WAL is attempted. Cross-store network partition and power-loss proof remain open.

Next S240: combined live authority and broker failure injection on prepare-only and committed-orphan paths, with strict recovery differentiation.
