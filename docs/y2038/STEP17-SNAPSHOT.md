# Step 17 — Committed-ledger snapshots, restore, and compaction

Run `python3 docs/y2038/step17_snapshot.py`.

Single-node implementation: canonical SHA-256 chained entries, snapshot of committed prefix, digest-checked restore, fsynced atomic file replacement with directory sync, compacted anchor, continued append using original chain head, rejection of stale and uncommitted snapshots.

Local test: 8/8 checks passed, including tamper detection and post-compaction continuity. The hash digest is not a signature and does not protect against an adversary who can replace both snapshot and digest. A compacted anchor requires independent trust for historical integrity.

**Not a distributed Raft snapshot installation protocol.** No follower InstallSnapshot RPC, durable consensus commit index, per-replica snapshots, snapshot quorum, persistent anti-rollback manifest, backup retention, or multi-host restoration. Do not infer production distributed durability from these checks.

Next milestones: Step 18 failure injection, Step 19 formal plus multi-host verification, Step 20 operational release gates.
