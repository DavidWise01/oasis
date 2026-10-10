# SHEET 161 — Live Indexed Witness Recovery and Benchmark

**Status:** `0e / PASS` for **36/36 new tests**. SHEET 160's isolated gate and migration tests passed **71/71** and **19/19**. The complete historical lineage was not rerun.

## Purpose

Connect the **S160 indexed Merkle physical journal** to independent **mTLS witness processes**. Recover a lagging physical witness from a 2-of-3 signed checkpoint without replaying the complete history at the recovery endpoint. Bind the operation to an independently signed and separately persisted high-water floor.

## Executable components

- `proof161.js`: validates 2-source signed checkpoint quorum, external anchor, exact record hash, every indexed inclusion proof, and the Merkle extension against the receiver's own retained frontier.
- `node161.js`: per-process mTLS witness endpoints `/head161`, `/page161`, `/begin161`, `/apply161`, `/status161`, `/finish161`. Uses `baseline160/indexed160.js` for actual durable writes. Each page is bounded to **8 records** to fit the inherited 16 KiB request limit.
- `catchup161.js`: an mTLS orchestrator that resumes after process failure from a persisted nonce/cursor and never assumes an acknowledgement implies durability.
- `gate161.js`: 36 assertions using real TLS processes, forged pages, rollback, restart, signer quorum and verified network recovery. Generates `benchmark161.json`.
- `benchmark161-small.json` and `benchmark161-large.json`: other independently measured workloads (earlier version of the 35-check test harness).
- `BENCHMARK-REPORT.md`: quantitative comparison, test method, constraints and next bottleneck.
- `KERNEL-ASCII.txt`: full process and adversarial branches.

## Reproduce

```bash
cd sheet161
bash run-new.sh
# More rows, using environment variables
S161_SEED=4096 S161_PREFIX=3072 node gate161.js
```

Requires Node.js 22+, OpenSSL CLI and Linux/POSIX fsync filesystem semantics. On each run, synthetic Ed25519 identities and short-lived mTLS certificates are generated in a temporary directory and removed afterward. The benchmark includes page proof computation, network round trips, TLS handshakes per request and per-row durable writes.

## Preserved lineage and observed limits

`baseline160/` is a byte-for-byte preserved SHEET 160 release tree. The **71/71** standalone SHEET160 regression gate and **19/19** migration bridge passed in a separate copied tree. The attempted 12,288-record inherited benchmark timed out around 6,144 writes, so its 619 records/second result from the prior release is historical, not a fresh measurement this turn. Full historical regression chain was not completed.

No independent data centers or physical hosts were used. The external checkpoint is signed separately but stored on the same test host, and is not a trustless public transparency anchor. Inclusion proof validation is independent of the source index's claims *given* a sound externally certified Merkle root, but it does not prove physical disk persistence to an independent auditor.