# KET ROSE V5 — Interrupted transfer and idempotent replay

Append-only successor to V4 reversal and replay. Fixed origin `0vwxyz`; 8 Gen0–2 paths × 3 H/O/N bands = 24 identities. Phase ring is 60 positions; the shadow remains optional/unresolved.

Windows: `122–125`, `140–145`, `360–366` (17 included slots, 14 adjacent links). Each link transfers 2.5% of the current source balance to its destination. Aggregate balance stays at 36,600 units.

V5 simulates interruption before PREPARE, after PREPARE and between debit and credit for each of the 14 links (42 scenarios). PREPARE and ABORT leave balances intact; the COMMIT step makes both balance changes together. The idempotency key is `rose-v5:{edge}:{source}->{destination}`. Recovery replays all links, skipping committed keys. Journal receipts and the canonical final SHA-256 state digest must match the uninterrupted run exactly. Repeating recovery is a no-op.

**Results: 42/42 scenarios PASS; 14 exactly-once commits; zero net balance loss.** Run `python recovery_v5.py`.

Limit: this is in-memory atomicity simulation, **not** durable write-ahead logging or real power-loss recovery. Physical force, photon and sub-Planck interpretations have not been demonstrated.
