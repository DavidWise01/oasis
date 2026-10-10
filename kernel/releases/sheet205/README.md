# SHEET 205 — Challenge-Bound Snapshot Freshness

**Local focused gate: 15/15 PASS** (`python gate205.py`) using original S176 Node WAL and S179 SQLite target. A signed evidence statement binds challenge nonce, prior floor hash/generation, target and WAL heads. The local SQLite floor enforces TTL, a second freshness check, replay prevention, and monotonic generation. Injected target mutation before final validation fails closed. Source ZIP `SHEET205-challenge-freshness.zip` (68,414 bytes) SHA-256 `d1d401dfaf37b0cbd53ade9966138267beb633c2926356ebbeb93a266c5e36a1` includes exact test runner and inherited S204 source.

**Boundaries:** Not integrated into the live S195/S203 mTLS floor. WAL and DB are not read atomically and may change after final recheck before floor commit; concurrent production safety not proven. No host partition, power loss or historical regression rerun. Test modifies and restores fixture data only.

Next SHEET 206: separately issued mTLS floor challenge and storage fence covering authorization.
