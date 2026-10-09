# SHEET 150 — Replica-Verified Durable Journal Inclusion

**Status:** 84/84 new fault-injection checks passed. The full preserved SHEET 149 runner also exited with status zero in this run (1,114 inherited checks, 1,198 total using release-level arithmetic). All inherited source files are copied unchanged.

## Change summary

SHEET 149 authenticated signed resource receipts but did not require evidence that a receipt was represented in the resource journal. SHEET 150 adds a separately signed resource checkpoint, a Merkle inclusion path for the exact record hash, and an append-only prefix witness pinned by the replica journal.

- `journal150.js`: domain-separated Merkle root and path verification, Ed25519 signed checkpoint verification, and bounded full-prefix comparison.
- `resource150.js`: actual mTLS-protected resource, SHA-256 record chain, signed journal checkpoint, `/proof` endpoint, and crash-safe idempotent write retry.
- `replica150.js`: new persistent replica state schema, inclusion/prefix checks at both prepare and commit, replay checks after restart, and per-resource high-water pins.
- `bridge150.js`: passes the complete signed receipt and journal proof into the replicated COMPLETE proposal.
- `gate150.js`: 84 checks including real subprocess TLS, invalid proofs, validly signed forked histories, process crash, leader handoff, and rollback.
- `index.html`: read-only interactive SVG fault viewer; displays synthetic verified fixtures, not connected telemetry.

## Verify

```bash
node gate150.js
bash run-all.sh
```

`run-all.sh` runs the preserved SHEET149 suite and then SHEET150's new suite. Full inherited runs are comparatively slow and previously had a timing-sensitive assertion in the SHEET142 lineage; any regression run should be repeated before claiming stable CI reliability.

## Proof format

A checkpoint signs `{schema,resourceId,sequence,resourceHead,root,count}` with `S150:CHECKPOINT`. Each proof carries an inclusion path and the complete list of committed record hashes as a bounded prefix-consistency witness. Replica verification requires both the signed checkpoint and an inclusion path for the exact receipt sequence and record hash. The retained hash list detects a re-signed divergent prefix across successive completions. The verifier rejects missing signatures, altered Merkle siblings, swapped entries, decreasing sequence, and conflicting roots at the same sequence.

The tree duplicates the odd terminal node at each level; **this is a defined local construction, not an RFC 6962 compatible Merkle tree.** The complete prefix witness is O(n), not a compact Merkle consistency proof, and is limited to 128 records per resource in this demonstration. It must be redesigned for a production unbounded journal. Hashing and signatures prove consistency with *signed assertions*, not that untrusted hardware actually durably wrote the bytes. A compromised resource signing key can certify invented data, especially for an unpinned initial journal.

## Security boundaries

- Three real mTLS authority processes and one mTLS resource process, all on one physical host.
- Development CA and Ed25519 keys, no independent host operators, no live outside trust anchor or production authorization.
- Hashes depend on JSON property order in the inherited protocol; cross-language canonical serialization remains a migration task.
- Local fsync + atomic rename used for journal state. No hardware-failure durability guarantee.
- The prior SHEET142 intermittent concurrency test remains a known quality issue.
- Existing SHEET149 binary/state schema intentionally preserved; no in-place migration performed.
- Original SHEET103 golden-fixture compatibility still not verified.

## Follow-on target

SHEET151: independently anchored checkpoint snapshots, compact scalable append-only consistency proofs, and a reset/migration gate for bounded journal rollover.