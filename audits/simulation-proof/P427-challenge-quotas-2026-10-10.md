# ROOT0 P4.27 — bounded challenge quota (2026-10-10)

Node v22.16.0, local SQLite regression **27/27 assertions PASS**, repeat elapsed **44.431 ms**. P4.27 extends P4.26 durable nonce verifier with transactional maximum outstanding challenges, persistent per-deployment rolling issue quotas, automatic expiry on issuance, and bounded retention garbage collection. Replay of a consumed challenge remains rejected after verifier restart. After garbage collection, deleted nonce remains unsolicited and therefore rejected.

Synthetic 1,000-request burst, configured outstanding maximum 32: **32 issued, 968 denied**, pending SQLite rows 32. Quota persisted over restart; expiry and quota renewal tested. No network load generation, independent-host trust, clock-tamper resistance, or resource exhaustion proof. Both issuance and existing verifier use SQLite BEGIN IMMEDIATE.

Open issues: SQLite storage and quotas remain in local host trust domain. Date.now() is not a trusted monotonic source, and an administrator can change the clock. Retention/pruning runs on issue or explicit cleanup only; a scheduled janitor is needed in idle periods. Quota limits are per database and not globally shared across independent verifier databases. A production cleanup policy should track all deployments independently.

Runnable tested files `p426_core.mjs`, `p427_quota.mjs`, `test_p427.mjs`, JSON and README are in attached ZIP SHA256 `010aaba4612ac2952ced5049fc2b938997bd0f4a949454fb6fd3ecffa801dac8`.

Next P4.28: monotonic elapsed-time and checkpoint reconciliation rules, cleanup under concurrent multiprocess load, and proof that quotas cannot be bypassed with cross-deployment databases.