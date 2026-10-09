# SHEET 140 — Joint-Consensus Membership and Fencing

**Status:** `0e / PASS` — 63 new synthetic regression checks. This layer is additive to frozen SHEET 139 (764 inherited checks). This is not multi-host or production certification.

## Purpose

SHEET 139 requires **all deployed custodians** to persist and sign the same policy. SHEET 140 provides an explicitly approved membership transition, without automatically treating a failed member as optional. For the test replacement `GREEN -> AMBER`, the old set is `{RED, BLUE, GREEN}` and the new set is `{RED, BLUE, AMBER}`.

A transition must pass these gates:

1. Active old fleet is verified by SHEET 139, with every required custodian represented.
2. Two current operator signatures approve an exact proposal body and expiration.
3. The replacement node proves possession of its signing key.
4. **All old members** sign `JOINT_OLD` and **all new members** sign `JOINT_NEW`. The union is four distinct node identities for this example; overlapping IDs sign both roles.
5. **All new members** sign `FINAL_NEW` as a distinct authorization phase.
6. A separate SHEET 139 new-fleet register must already be verified with the new member set.
7. The Mother Kernel atomically switches local membership history to the new head and increments the monotonic fencing token. Previously issued lease credentials become invalid.

The transition is **blocked** if an old required custodian is permanently unavailable. SHEET 140 intentionally provides no unilateral replacement, quorum downgrade, or automatic break-glass authority. Such a recovery mechanism would require a separate, explicitly reviewed security policy.

## Run

```bash
cd sheet140
node gate140.js
bash run-all.sh
sha256sum -c SHA256SUMS
```

Requires Node.js 22+, Python 3, Bash, and OpenSSL for inherited tests. The new tests use ephemeral Ed25519 credentials, local files, and signed SHEET 139 test fleet receipts. Browser demo (`index.html`) is a precomputed scenario explorer, not a live administration console.

## Files

- `membership140.js`: signed proposal, old/new joint approvals, separately finalized membership cutover, hash-linked local state, signed expiring fencing leases, and fail-closed authorization guard.
- `gate140.js`: 63 tests for authorization, old/new membership, interruption, changed pins, stale leases, signers, fork quarantine, and historical hash continuity.
- `baseline139/`: **pristine** inherited SHEET 139 release, with its dependent full baseline lineage.
- `run-all.sh`: isolated inherited tests followed by SHEET 140 tests.
- `index.html`: SVG architecture and interactive scenario explorer.
- `KERNEL-ASCII.txt`, `release-receipt.json`, `SHA256SUMS`: architecture and evidence.

## Security boundaries

- **Local fencing, not distributed fencing**: the monotonic token is verified by the cooperative local authorization guard. For distributed correctness, **every protected remote resource** must independently reject older tokens, with a consistent source of authority.
- **Not distributed joint consensus**: this is a deterministic signed joint-approval barrier, not a complete Raft/Paxos consensus implementation with formally proved safety/liveness.
- **Not automatic failed-node replacement**: an unavailable old member holds the transition indefinitely until it can attest or separate recovery governance exists.
- **Wall-clock expiry** is a local guard only; no independently trusted time source is established.
- **No production credential custody, no remote network isolation, no external anchor service**.
- Existing SHEET 139 membership never mutates in place. A new fleet is independently certified, and the new membership head refers to that separately verified certificate.

## Next target

SHEET 141: independently enforced distributed fencing at protected resources and a formally specified emergency recovery procedure that cannot be mistaken for routine reconfiguration.