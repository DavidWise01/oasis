# Harvester v16.1 — Task 01: Durable Commit Journal

Status: **IN PROGRESS / DESIGN CHECKPOINT**. This file does not claim an implemented or benchmarked journal.

## Scope
Add a crash-recoverable commit ledger to the v15 dual-path 40-bit / 10-ACK protocol, without altering its transport semantics. The 12-bit projection is observational only and must never repair bytes.

## Authoritative identifiers
- `transfer_id`: stable across retries for one logical 40-bit payload.
- `attempt_epoch`: strictly monotonic across retries, rejecting earlier ACKs.
- `payload_sha256`: SHA-256 of the exact five source bytes.
- `acks`: exactly five witnesses per path; each witness binds transfer ID, attempt epoch, path A/B, position 0..4, and source-byte digest.
- `delivery_key`: stable across recovery and retries of **the committed** transfer, suitable for receiver-side deduplication.

## States and permitted transitions
```
NEW -> PREPARED -> COMMITTED -> RELEASE_PENDING -> CONFIRMED
                         \----> QUARANTINED  (on corruption / integrity mismatch)
```
- `PREPARED` requires ten valid current-attempt ACKs and matching source.
- `COMMITTED` is established by an atomic durable write, never merely RAM state.
- `RELEASE_PENDING` retains the same delivery key during retry/recovery.
- `CONFIRMED` requires a receiver receipt bound to delivery key and payload hash.
- Replayed transitions must be idempotent; conflicting payloads/epochs must be rejected.
- Incomplete prepared entries may be abandoned and retried with a new epoch; committed records cannot be silently rolled back.

## Crash boundaries
1. Before prepare: no output.
2. After prepare, before durable commit: no output.
3. After durable commit, before receiver call: recover committed record and continue.
4. After receiver effect, before confirmation persisted: re-send same delivery key; the receiver **must** deduplicate before applying another effect.
5. After confirmation: never reapply effect.

## Persistence contract
Store implementations must provide atomic compare-and-swap or a single-writer transaction spanning state, payload digest, ACK witness set, and idempotency key. A loosely ordered sequence of localStorage writes is **not** sufficient. For browser deployment, prefer IndexedDB transaction; verify actual durability and behavior separately in Chromium.

## Task-01 acceptance checks
- A packet from an earlier epoch is rejected.
- Missing ACK or missing byte rejects PREPARE.
- Replay and duplicate ACK cannot inflate quorum.
- Corrupted source/digest rejects commit.
- Invalid state transition rejected.
- Persistence failure prevents output release.
- Journal rehydration preserves committed identity and delivery key.
- Two contenders cannot commit conflicting payloads for one transfer ID.

## Dependencies and next tasks
- #2 Crash injection and deterministic recovery.
- #3 Receiver-side deduplication and reconciliation.
- #4 Inherited tests / Chromium desktop+mobile.
- #5 Evidence manifest, freeze after **new** passing results.

No new passing test counts are asserted by this checkpoint.
