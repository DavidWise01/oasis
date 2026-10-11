# SHEET 225 — Read-Only WAL Access for Separate Repair UID

Executed `python gate225.py` on Linux as root test harness: **18/18 PASS**. WAL directory owned by writer (`daemon`, UID 1), mode `0750`, WAL mode `0640` — repair identity (`nobody`, UID 65534, group daemon) may read but cannot append, truncate, rename, delete, chmod or create alongside WAL. Repair has separately owned DB directory mode `0700` and SQLite repair DB mode `0600`. Writer cannot read repair DB. Authorized writer appends; repair commits separate SQLite binding. Both remain within assigned directories.

**Exact runnable artifact:** `SHEET225-wal-readonly-repair-isolation.zip` (113104 bytes), SHA-256 `5baf9a05ecc426b3f6607800d9f5ffe6622e089007875b874a81f41270e35e18`, includes `gate225.py`, `README-SHEET225.md` and S224 predecessor ZIP. ZIP integrity check passes.

**Scope limitation:** This verifies *filesystem discretionary permissions only*, not a full S224 signed mTLS crash-recovery rerun with the new layout. Root or same writer UID still controls WAL; no power-loss/distributed atomicity proof. Next S226: complete signed recovery under this layout and run before/after-commit crash gates.