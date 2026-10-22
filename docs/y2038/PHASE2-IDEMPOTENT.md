# Phase 2.4 — idempotent IT3 write and readback boundary

A create-only etcd transaction can return a conflict on retry even if the original commit succeeded. A timeout can also mean an unknown commit result. This module resolves both through a **linearizable** read of the stable key, accepting an existing record only if the exact canonical IT3 bytes match.

No receipt is returned when the linearizable read fails. Same key + different bytes produces `IdentityConflict`. This eliminates accidental overwrites for a fixed record ID, not arbitrary concurrency risks in a wider application.

Run: `cd docs/y2038 && python3 check_phase2_idempotent.py` (12 mock assertions).

**Production evidence is still missing.** The mocked backend is not a live three-node cluster. Phase 2.3 remains the executable local Docker fixture, which uses insecure test-only HTTP; real deployment needs mTLS, genuine leader-loss tests, persisted evidence, backups, and independent review. The Step 20 release gate stays BLOCKED.
