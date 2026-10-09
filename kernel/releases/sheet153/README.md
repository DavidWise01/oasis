# SHEET 153 — Unified Physical Journal / Durable Finality Barrier

**Status:** new standalone gate `43/43 PASS`. Inherited total and release attestations are in `release-receipt.json`; do not infer production safety from simulation checks.

## What changed

SHEET 152 used two disjoint histories: a capped S150 physical resource state plus an S151 segmented evidence ledger. SHEET 153 replaces that split in the **new resource153.js and replica153.js path**. The S151 segmented journal now contains the actual resource operation payload, and the signed resource receipt refers to its physical record hash. The authority's replicas verify that SAME record using a single S151 Merkle inclusion proof, the resource's Ed25519 checkpoint, and a live snapshot from the independently running anchor signer. The proof is no longer limited to 128 records.

`unified153.js` creates physical journal payloads with immutable transaction identity, operation, epoch, grant-head and digest. `resource153.js` retains the live mTLS majority checks before the write, controls local serialization, and returns an idempotent receipt on retry. `proof153.js` checks the signed receipt, physical payload, chain record, inclusion proof, signed checkpoint, independent anchor signature, and monotonic history pins. `replica153.js` independently replays the verification during prepare, commit, and journal load. `bridge153.js` rejects unanchored completions.

`finality153.js` serializes cooperating coordinator instances with a durable local intent ledger and exclusive file lock. Its transitions are `INTENT -> ANCHORED -> DONE`. An interrupted anchor advance can be reconciled with the exact previously recorded transaction and checkpoint. During that uncertainty the certified pending grant prevents a membership cutover. A real process crash leaves an orphan lock requiring separate manual review; the controller does **not** steal or remove it.

## Run

From the extracted `sheet153` directory:

```bash
node gate153.js
bash run-all.sh
```

The suite creates local RSA TLS test certificates and Ed25519 signing keys using OpenSSL. It uses three separately running mTLS authority processes, an mTLS resource process, and an independently running mTLS anchor signer on **one computer**.

## Scope of the test

The suite inserts **258 synthetic fixture records directly into the physical segmented store** to cross the old 128-record limit, then performs **three real quorum-authorized mTLS writes** at records **259, 260 and 261**. The resource is actually killed after durable write 260 and relaunched; the original receipt is recovered without a duplicate append. Additional fault injection covers a failure after anchor advancement and a separate failure between advancing the anchor and persisting the controller's ANCHORED state. An old leader, invalid grant, stale anchor snapshot, substituted Merkle branch, changed segment, and unavailable anchor are rejected in local tests.

**Trust boundary:** The new physical journal is directly connected to the new replicated authority path; it does not modify the prior immutable SHEET 152 code. It retains the original S151 128-*per-segment* structure rather than a 128-*total* limit.

**Not proven:** There is no cross-host atomic anchor/quorum transaction. Anchor movement still precedes majority completion; the durable controller ledger and outstanding grant provide fail-closed recovery for cooperating local participants, not an external distributed transaction proof. The first 258 test fixtures bypass the grant protocol intentionally. Resource durability means validated fsync/atomic protocol in this development environment, not independent power-loss validation. Historical SHEET 142 intermittent test remains a known inherited issue.

For full route, processes, exits, recovery branches and known proof limits see `KERNEL-ASCII.txt`.