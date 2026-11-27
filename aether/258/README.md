# AETHER-258-RS — Actual SQLite CAS Concurrency & Durable Local Receipts

This phase runs real concurrent connections against a local SQLite ledger using BEGIN IMMEDIATE and WAL with synchronous=FULL. A contender can accept only if its expected sequence and head match the current stored values. Accepted events are append-only with UNIQUE challenge and nonce fields; all attempts, including stale rejections, receive deterministic SHA-256 receipt hashes in a separate append-only attempts table. The latest head is mutable as the CAS pointer; history rows are not updated.

A barrier launches 2 to 32 independent connection contenders with the SAME prior head. Under a functioning local SQLite transaction lock, exactly one contender can accept. Unit tests exercise 2, 8, and 16 workers, rollback on duplicate attempt ID, replay of challenges and nonces, and chain continuity.

Run:

    python3 -m unittest discover -s aether/258 -p 'test_*.py' -v
    python3 aether/258/sqlite_cas.py --db /tmp/aether258.db --workers 8 --out /tmp/aether258.json

WARNING: use a dedicated local scratch DB file. This program writes new local SQLite files, deliberately performs CAS transactions, and does not interact with production data or external networks. The harness is not a multi-host distributed CAS: separate host processes must point to one real atomic service, and SQLite WAL on network filesystems is not a substitute. Local FULL synchronous settings do not independently demonstrate power-loss durability or external immutable custody. No external signatures or independent witness roots are proven. This tool cannot authorize ACT.

History phases XVIII and XIX remain unchanged. Operational authority HOLD, physical qualification 0%.

Next AETHER-259-RS: multi-process contention with immutable transaction receipt export, receipt hash verification, and crash/restart recovery before any external service claim.
