# P3.70 Transactional SQLite signing anchor

2026-10-09: P3.69's per-file anchor is superseded by a prototype using Node 22 node:sqlite DatabaseSync, WAL, synchronous FULL and BEGIN IMMEDIATE transaction to atomically update vote records and checkpoint metadata. Explicit upstream trusted checkpoint must match stored count and head before a new epoch is reserved. A stale trusted checkpoint and replacement empty database fail closed. The outer symbolic topology remains -+5 + 1.

Executed Node v22.16.0 regression PASS 111 assertions: 101 write transactions, same-epoch refusal, repeat vote, reboot, 100 sequential additional reservations, replay, stale external state and empty-store rollback. **No independent-process race test has been run**. The prototype's trusted checkpoint is still supplied and updated in memory, not persisted independently. SQLite WAL sidecars and filesystem fsync properties vary; simultaneous rollback of external checkpoint and database remains unsolved. No claim of production durability or distributed consensus.

Next P3.71: separate-process contention and durable externally sealed watermark, ensure atomic checkpoint publication.
