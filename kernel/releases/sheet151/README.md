# SHEET 151 — Compact Journal Consistency and Independent Checkpoint Anchor

**Release:** `0e / PASS` — 64/64 new checks; inherited SHEET 150 runner exited 0. The inherited lineage comprises 1,198 test assertions on the preceding release's accounting, for a combined **1,262/1,262** on this execution. The inherited SHEET 142 timing-sensitive assertion has not been repaired, despite passing here.

## What's new

SHEET 150 capped the **entire resource history** at 128 hashes and required the verifier to receive all historical record hashes for prefix consistency. SHEET 151 changes the new *additive* journal format: each durable disk segment contains at most 128 records; the overall demonstration crosses 518 records. An incremental binary-peak hash accumulator represents the whole history and produces compact append-extension blocks and receipt inclusion paths.

- `merkle151.js`: domain-separated binary-peak Merkle forest, append via peak merges, compact aligned suffix-cover proof, and O(log N) inclusion path; proof verification does not receive a full prefix history list. The proof *generator* still reads the hash history.
- `ledger151.js`: segment rollover, SHA-256 record-chain integrity, atomic segment and head files, explicit torn-write detection and fail-closed local single-writer lock, signed checkpoint generation.
- `anchor151.js`: independent signer key, durable signed monotonic checkpoint floor, signature and consistency proof verification, rollback/fork rejection.
- `anchor-server151.js`: separate local signer process via trusted Node IPC. Resource private signing key is not loaded by anchor process and anchor signing key is not loaded by resource Ledger.
- `gate151.js`: 64 tests covering 128/256/512 rollover, 518 records, inclusion across segments, failed proofs, anchor restart, signed fork, replays, restored old journal, corrupt segments, crash window, and orphaned writer lock.
- `index.html`: interactive, offline SVG fault scenarios and JSON export. The dashboard displays verified test fixtures, not live process telemetry.

## Run

```bash
node gate151.js
bash run-all.sh
```

`run-all.sh` runs a copy of the preserved SHEET 150 test tree, then the new SHEET 151 gate. The baseline is included under `baseline150/` and never intentionally modified by SHEET 151.

## Protocol

A resource checkpoint signs `{schema,resourceId,count,root,lastRecordHash,previousCheckpointDigest,segmentSize}` with domain `S151:CHECKPOINT`. The independent anchor verifies the resource signature, checks that the previous checkpoint digest exactly matches the current trusted anchor, confirms strictly increasing record count, verifies the compact aligned-block append extension against the old signed frontier, and signs the new monotonic floor using `S151:ANCHOR`.

The append extension carries one hash per aligned complete perfect subtree covering the new suffix. Depending on sequence positions the witness is O(log N) hashes, rather than SHEET 150's complete O(N) prefix witness. Receipt inclusion proofs include one sibling per level in the relevant binary peak and the other peak roots. The custom tree and peak-bagging construction is **not RFC 6962 compatible**; no formal cryptographic security proof or third-party protocol audit is claimed.

## Durable behavior

Writes first atomically replace a segment file, then atomically replace the head file. A crash between those two operations creates a discrepancy: reopening fails closed with `SEGMENT_COUNT_OR_TORN_WRITE`, and writes stay blocked until a reviewed recovery protocol resolves it. A local `wx` writer lock prevents simultaneous cooperating appenders; orphan locks are not removed automatically. There is no automated repair path in this release.

The signer is a separate **process on the same machine** and its IPC interface currently trusts its parent. It is not network-isolated, mTLS authenticated, or production safe. Signed floors protect against local history rollback only while an independently retained *current* anchor remains available and its key/file are not rolled back together. Resource/anchor file-system separation is simulated, not enforced by OS privileges. A compromised resource signing key can certify fabricated history, and hashes cannot prove physical disk durability.

## Compatibility and performance limits

The SHEET 151 format is new, not an in-place migration of the SHEET 150 replica/resource schema. It is an additive journal/anchor prototype, **not yet wired into the SHEET 150 network authority completion path**. JSON property order remains part of inherited signature and hash behavior. Index validation rereads and rehashes all segment files for every write, so storage I/O and CPU remain O(N) per append, despite O(log N) proof size; future releases should add authenticated cached segment indexes and idempotent transactional migration.

Legacy SHEET 142 intermittent assertion, original SHEET 103 compatibility, independently operated physical hosts, hardware WORM, multi-writer fencing and distributed anchor consensus remain unverified.

## Next target: SHEET 152

Connect the anchored checkpoint verifier to each replica's `COMPLETE` path, implement crash-reviewed reconciliation of torn segment/head writes, and test malicious leader proof substitution across actual mTLS services.