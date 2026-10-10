# SHEET 181 — Crash-Consistent Three-History Recovery

New local gate: **19/19 PASS**, executed using `python gate181.py`.

Artifact: `SHEET181-crash-consistent-three-history.zip`, SHA-256 `fe5b693ed8940d3152778dd412a9ae42faa89bffb9da4bc86f987631b10d1c8c`, 6327 bytes. Executable files in ZIP: `atomic179.py`, `signed180.py`, `coordinator181.py`, `gate181.py`, `README.md`.

The local coordinator durably persists one prepared request, atomically commits an idempotent SQLite target record, separately persists a signed Ed25519 target head, and removes the prepare marker. It quarantines missing signatures, stale heads, tampered prepares, missing target commit and unresolved crash windows. An operator must explicitly initiate reconciliation; no automatic uncertain commit.

**Verified boundary:** 19 local checks; no inherited suite rerun on this release, no actual hard-kill or power-loss test, no physical host independence, no complete S176 WAL integration, and no proof of distributed exactly-once semantics. Signing and target commit remain non-atomic; fail-closed reconciliation handles their gap.

Executable source is in the accompanying ZIP, not in this GitHub commit. Next: SHEET 182 hard-kill boundaries, cross-process fencing and inherited S176 WAL integration.
