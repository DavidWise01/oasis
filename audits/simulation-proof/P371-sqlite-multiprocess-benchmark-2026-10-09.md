# P3.71 — Transactional anchor multiprocess benchmark

Date: 2026-10-09. Runtime Node v22.16.0 using `node:sqlite` with WAL, synchronous FULL and BEGIN IMMEDIATE.

P3.70 baseline regression rerun: PASS 111 assertions and 101 reservations.

**Measured local process tests**, separate SQLite DB per concurrency level; all workers launched with original genesis checkpoint:
- 1 process: 1 accepted; 47.43 ms; database integrity ok
- 8 processes: 1 accepted; 7 checkpoint mismatches; 82.13 ms; integrity ok
- 32 processes: 1 accepted; 30 checkpoint mismatches and 1 exception; 347.10 ms; integrity ok
- 64 processes: 1 accepted; 63 checkpoint mismatches; 609.96 ms; integrity ok

Sequential reservations:
- 100: 6.77 ms, 14772.8 writes/s
- 1000: 61.85 ms, 16167.3 writes/s
- 5000: 282.95 ms, 17671.1 writes/s
All 6100 accepted; all reopened databases matched the trusted checkpoint.

Stale-checkpoint reuse rejected (checkpoint-mismatch). Replacement empty database with retained trusted checkpoint rejected (checkpoint-mismatch).

**Interpretation:** First concurrent writer progresses; all other writers with independently stale genesis state fail closed. This prevents an untrusted stale checkpoint from silently becoming accepted, but means the prototype is NOT a multiwriter transaction service. Need authoritative serialized checkpoint publication/refresh to enable concurrent progress, with prevention of checkpoint rollback. The single exception during the 32-process test needs investigation (possibly SQLite startup/lock contention); do not assume a cause. No externally durable trust, full power-loss guarantee, or consensus proof. Results are single-environment local measurements.

Source stress harness and machine-readable results are available in conversation deliverables.
