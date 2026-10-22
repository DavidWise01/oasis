# Step 11 — {{i}} distributed-ledger path

Status: **quorum prototype verified locally, NOT a fully durable distributed ledger**.

## Canonical path

`/vogel/voxel/vector/sda/{drive}`, read right to left.

```text
{{i::time::ledger::v1}}
  IT3 signed time → canonical 16-byte payload
  → append-only record {term,index,prior_hash,payload}
  → SHA-256 hash chain
  → quorum acknowledgment
  → committed prefix → replica recovery
```

Three nodes A/B/C; a majority of two is required to mark a record committed. A minority write may be staged but is not committed. The executable Python model simulates quorum decisions, hash verification and replica catch-up; it uses in-memory replica logs and is deliberately **not** a real network, consensus or storage engine.

### Tested
Run `python3 docs/y2038/step11_quorum.py`:
- majority commit; minority noncommit
- recovered majority commits
- hash chain verification
- payload tampering detection
- lagging replica catch-up

### Required to reach fully durable distributed ledger

1. Consensus protocol (Raft or equivalent) with elected terms, replicated log matching, fencing and no two concurrent leaders; no invented agreement based on acknowledgments alone.
2. Per-node disk WAL, fsync **before** acknowledgments, directory fsync for creations/renames, checksummed records and crash replay.
3. Preserve committed log prefixes across term changes and never overwrite committed entries.
4. Authenticate peers with mTLS and authorize cluster membership changes through joint consensus; message replay prevention.
5. Resilient snapshots, backups/restore, integrity proofs, retention and disk-full/backpressure handling.
6. Fault-injection across leader crashes, network partitions, power loss, stale leaders, data corruption and non-atomic storage.
7. Formal safety/liveness model checking and multi-host evidence, with clearly defined failure model (crash faults vs Byzantine).
8. CI gate that blocks deployment until fault and restart suites pass.

Hash chaining detects modification only when the expected head is independently trusted. It does not alone establish Byzantine fault tolerance, data availability, or cryptographic provenance.

No service is running and no claim of production durability is made.
