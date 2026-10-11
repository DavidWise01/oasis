# SHEET 224 — Split-Identity Repair and Dual Crash Boundary

**Executed:** `python gate224.py` 39/39 PASS (Linux test harness with root setup). Writer UID `daemon` (1); separate repair UID `nobody` (65534), with group `daemon` (1). Writer cannot open the mode-0600 repair socket in repair-owned mode-0700 directory. Original signed Node WAL, S218 input ledger, S220 service, local mTLS target/floor and signed orphan reconciliation all execute in one run.

Actual SIGKILL before repair SQLite COMMIT preserves previous WAL binding and rolls back floor generation. Actual SIGKILL immediately AFTER SQLite COMMIT preserves the completed binding; retried signed request is rejected as already applied. Protected writer subsequently resumes.

**Full exact-tested ZIP:** `SHEET224-split-identity-commit-boundary.zip` (119905 bytes, 83 files), SHA-256 `0eca2c6e1ffca9e65f657e666dbe669fd5f88e92765bc82b1ba2c45a14f14273`. Includes `gate224.py`, `build_gate224.py`, `repair224.py`, `reconcile224.py`, README and 223 predecessor code. ZIP integrity verified.

**Open vulnerability:** the shared group-writable private directory lets repair process access WAL storage beyond intended privileges. Thus this is NOT a least-privilege storage separation gate. Local fixture CA, root test harness, no physical power loss, cross-store atomicity or independent operators. Next S225: split WAL directory read-only from repair DB write authority, use narrowly scoped repair-mediated DB operation.
