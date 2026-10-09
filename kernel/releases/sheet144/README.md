# SHEET 144 — Quorum-Authorized Recovery Controller

**Status:** `0e / PASS` on **56/56 SHEET 144 checks**, plus **901/901 inherited checks in the latest isolated regression run** (combined 957/957). The frozen SHEET 142 test suite previously exhibited an intermittent simultaneous-request scheduling assertion. That sensitivity remains an inherited limitation; the successful run is not proof the flake has disappeared.

## Scope

SHEET 143 preserved an orphaned transaction lock after a hard crash and required manual inspection before clearing it. SHEET 144 makes that inspection and decision auditable through a **2-of-3 Ed25519 operator approval requirement**, an exclusive local recovery lock, durable decision states, and idempotent reconciliation of a **pre-existing** resource receipt.

SHEET 144 does not create a new resource write during recovery. It does not automatically release orphan locks on a timeout.

## Recovery state machine

`READ_ONLY_INSPECTION -> PLAN -> 2/3 SIGNED_APPROVAL -> APPROVED -> UNLOCKED -> RECOVERED`

An approval signs the exact transaction ID, request hash, existing resource receipt, local membership head and fence, external signed pin digest, orphaned lock identity, purported dead PID, and short expiry. All evidence is rechecked under an exclusive recovery decision lock before lock removal. An operator may sign a plan with the `recovery144.approval()` helper. The executor checks the operator public-key roster. A duplicate operator ID never counts twice.

An `APPROVED` event is durably written *before* the exact approved lock directory is removed. An `UNLOCKED` event is then stored, followed by the inherited `txn143.reconcile()` and an immutable `RECOVERED` event. If execution stops between removing the lock and writing `UNLOCKED`, rerunning the same approved plan deterministically resumes without applying the resource write again.

## Adversarial tests

The new gate covers:

- A real SIGKILL after the inherited resource has saved its write but before transaction journal completion.
- Quorum verification and rejection of missing, duplicate, unknown, or forged operator signatures.
- Changed transaction payload, replaced lock inode, active membership lock, absent resource receipt, and invalid signed external pin.
- Failure injected after lock clearance, followed by successful resumed reconciliation.
- Concurrent recovery calls, proving only one wins the exclusive decision lock; loser can retry idempotently.
- SHA-256 linked decision journal tampering, signed checkpoint verification, rollback, and forgery tests.

## Files

- `recovery144.js` — additive recovery controller and signed checkpoint verifier.
- `gate144.js` — 56 security/recovery checks.
- `baseline143/` — byte-identical preserved SHEET 143 source tree and full historical test lineage.
- `run-all.sh` — tests inherited chain from a fresh temporary copy, then SHEET 144.
- `index.html` — interactive SVG scenario viewer and JSON evidence export.
- `KERNEL-ASCII.txt` — full tree and fail-closed transitions.
- `SHA256SUMS`, `release-receipt.json` — integrity and test results.

```bash
cd sheet144
node gate144.js
bash run-all.sh
```

Node.js 20+, Bash, OpenSSL and a filesystem with local directory-creation exclusion and atomic rename are required. The `baseline143` tree must be present alongside the SHEET 144 JS files.

## Critical safety limits

Operator approval authenticates an instruction; **it does not prove the crashed process can never restart**, especially on independent machines, in PID-reuse windows, or if the original locking protocol is bypassed. SHEET 144 checks that the supplied PID does not currently exist and requires an exact orphan lock fingerprint; this is a local demonstration, not a production-safe distributed lock revocation system. Separate fencing tokens must remain enforced at real protected resources.

SHA-256 integrity links alone do not provide external anti-rollback: the separate signed checkpoint must be independently stored and pinned by a trusted party to detect full-state rollback. The demo checkpoint and Ed25519 signing identities are generated locally. No independently hosted operator keys, production certificate authority, actual external publication, or globally linearizable distributed transactions have been demonstrated. Original SHEET 103 fixture compatibility remains unverified.