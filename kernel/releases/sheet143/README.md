# SHEET 143 — Crash-Recoverable Commit Coordinator

**Release state:** Executable local reference implementation. The new SHEET 143 gate currently passes 53/53 tests. SHEET 142's inherited 901 checks passed on an independent rerun. The first combined run hit a scheduling-sensitive inherited concurrency assertion; this is retained in the release notes rather than hidden. This is not production certification.

## Purpose

SHEET 142 holds one shared membership lock through each durable resource mutation but its separate journal could still lose a completion receipt during a hard crash. SHEET 143 attaches a persistent transaction ID and append-only decision journal to that existing locking/lease protocol.

## Transaction states

- `PREPARED` — request identity and validated lease recorded, resource not yet applied.
- `COMMIT_INTENT` — durable intent recorded; resource mutation may already exist after a crash.
- `COMMITTED` — durable resource receipt reconciled with append-only journal and hash chain.
- `ABORTED` — explicitly cancelled before any corresponding resource mutation.

All durable journal writes use the inherited atomic-file writer. Same operation ID cannot be assigned to two distinct transaction IDs. Retries of an already committed transaction return the original receipt without performing a second write.

## Crash window

`crash143.js` is test-only and deliberately sends `SIGKILL` to itself after the inherited SHEET 142 resource commit. The test verifies the resource mutation survives but its journal remains `COMMIT_INTENT`; the orphaned lock is retained and automated recovery fails closed. A human-reviewed lock release is demonstrated after checking process exit, signed pin, durable resource receipt, and transaction journal. Reconciliation only attaches that existing receipt.

This operator review is a *test protocol*, not a cryptographically authenticated operator-authorization workflow. No production process should delete an orphaned lock based solely on elapsed time.

## Signed transaction checkpoint

`txn143.checkpoint()` produces a locally signed Ed25519 body containing transaction journal count and head, resource sequence and receipt head, and current membership head/fence. `verifyCheckpoint()` independently checks signature, pinned journal prefix, and resource receipt prefix. A previous journal or resource state fails rollback checks; an alternative valid journal branch fails fork checks. Signing keys in tests are generated locally and are not externally held.

## Files

- `txn143.js` — append-only transaction journal, 2-stage decision handling, signed checkpoints, read-only recovery, explicit reconcile / abort.
- `crash143.js` — test-only hard-crash process.
- `gate143.js` — new end-to-end tests including SIGKILL, idempotence, tampering, concurrent writers.
- `baseline142/` — byte-preserved SHEET 142 release, including the full inherited chain.
- `run-all.sh` — run baseline in isolated temporary copy, then SHEET 143 tests.
- `index.html` — standalone SVG scenario viewer; visualization uses deterministic illustrated test states, not a live production network.
- `KERNEL-ASCII.txt` — full architecture.
- `SHA256SUMS` — contents of the release, with archive checksum separately provided.

```bash
cd sheet143
bash run-all.sh
```

Requires Node.js 20+, OpenSSL CLI, Bash, and local filesystem atomic-rename semantics.

## Safety limits

All cooperating writers must use the same shared membership and transaction filesystem locks; bypasses violate the proof assumptions. Separate physical machines, independent trust custody, transactional resource engines with external side effects, crash/power-loss durability on arbitrary hardware, fully automated lock recovery, and globally linearizable distributed commits are **not verified**. Original SHEET 103 historical parity remains unverified.