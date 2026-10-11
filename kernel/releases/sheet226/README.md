# SHEET 226 — Signed Recovery with Read-Only WAL Isolation

**Local integrated gate: 42/42 PASS**, `python gate226.py`. Executed S220 daemon-UID writer + S218 signed input ledger, S218 target/floor mTLS, S224 separate repair UID, real SIGKILL between WAL and SQLite and before/after repair commit. WAL directory is writer-owned mode 0750, WAL file mode 0640. The repair UID (nobody, daemon group) reads the WAL but fails to append and unlink it. The SQLite coordination database is separate from WAL storage, in a deliberately group-writable directory.

Precommit crash rolls back binding + repair-floor generation. Postcommit crash retains completed SQLite binding and rejects replay; protected writer resumes after valid reconciliation. The test harness provisions the WAL group-read mode after initial WAL creation.

**Exact tested runnable ZIP:** `SHEET226-readonly-wal-signed-recovery.zip`, 86 files, 126,526 bytes. SHA256 `bb9e8d2eb61e0fb01002bd9da8cb343f6dafb5b97119c5a977bc692849c5ff00`. Download from conversation to run gate226.py and its predecessors.

**Limits:** Linux root test harness; one host with generated test certificates; a privileged/root or writer-UID attacker can bypass OS DAC. Shared SQLite directory remains trusted mutable state. Not a cross-store atomicity, remote partition, or physical power-loss proof.

**Next S227:** independently isolate control DB writes through a broker or SQLite authorizer, and test mixed-service concurrent writes and power-interruption simulations.
