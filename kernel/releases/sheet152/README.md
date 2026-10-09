# SHEET 152 — Aligned Full-Pipe Anchor-Certified Completion

**Status:** new SHEET 152 gate `45/45 PASS` (test process exit 0). The inherited run and its actual exit code are documented in `combined-run.log` and `combined-exit.txt` when available.

## What changed

SHEET 152 connects the SHEET 151 independently retained segmented checkpoint to each SHEET 150 derived authority replica's `COMPLETE` validation. **No proof conversion is assumed:** S150 and S151 use different Merkle root formats. `anchor-proof152.js` creates a digest binding across the original S148 signed receipt, the old S150 resource checkpoint, and an indexed S151 segment ledger record. Every replica authenticates both the resource's Ed25519 key and an independent anchor Ed25519 key, checks its own persistent high-water mark, and queries the current independent signer head over pinned mTLS on every request.

The adapter implements an actual networked test with three authority services, one protected resource, and one independently running local anchor signer. The test kills and restarts the resource after a durable write, changes elected leaders, rolls the S151 ledger across 128- and 256-record boundaries, and attacks prepare and commit with forged votes/proofs. Reviewed recovery is separately tested for exactly one persisted-but-unacknowledged segmented record and requires two of three signatures.

## Run

Requirements: Node.js 22+, OpenSSL, POSIX filesystem.

```bash
node gate152.js
bash run-all.sh
```

`run-all.sh` copies `baseline151` into a temporary directory and executes the complete inherited chain unchanged before running the current gate. It does not rewrite the frozen lineage.

## Modules

- `replica152.js`: authority replica, complete-proof acceptance gate and replay validation.
- `anchor-proof152.js`: exact S150/S151 cross-format binding and Merkle verification.
- `anchor-server152.js`: mTLS checkpoint signer backed by SHEET 151's durable `Anchor`.
- `bridge152.js`: quorum coordinator with receipt and anchor proof attached.
- `resource152.js`: unchanged SHEET 150 resource behavior, with corrected nested import paths.
- `reconcile152.js`: quorum-authorized repair of one already persisted journal record only.
- `gate152.js`: end-to-end mTLS processes and fault-injection test.
- `KERNEL-ASCII.txt`: detailed 35-step execution path, topologies, fault matrix, recovery plan, and limits.

## Concrete security boundaries

1. A valid S148 receipt and S150 Merkle proof alone cannot complete a pending transaction in SHEET 152. Every replica also requires a signed S151 inclusion and *current* live anchor snapshot.
2. The old physical S150 resource still has its **128-record limit**. The S151 segmented journal scales beyond it, but the physical resource writer has not yet been replaced. Do not claim unbounded resource writes.
3. The running signer, authorities and resource are **separate processes on one physical machine**. This is not independent-host distributed consensus or proof of physical storage durability.
4. The signer can advance between a replica's current-head verification and durable commit. Cross-process atomicity between independent anchor changes and quorum completion is **not yet proven**.
5. The reviewed torn-write repair verifies two signatures and a supplied signed floor, but does **not** independently re-fetch a live floor while holding a distributed lock; production operators must treat that as an unresolved freshness gap.
6. Inherited SHEET 142 concurrency timing sensitivity remains an open regression issue.

## Next target

**SHEET 153:** combine physical S150 and shadow S151 append semantics, remove S150's 128-record limit, and serialize signer-floor movement with quorum-complete via a durable lease or an explicitly versioned checkpoint generation.