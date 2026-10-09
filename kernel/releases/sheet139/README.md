# SHEET 139 — Fleet-Wide Custody Synchronization Barrier

**Status:** `0e / PASS` on **764/764 regression checks**: 699 inherited SHEET 138 checks + 65 new SHEET 139 checks. Executable, synthetic, local multi-process integration; **not production certification**.

## Purpose

SHEET 138 added durable publication acknowledgement but did not guarantee that all custody processes had received and persisted the most recent revocation/enrollment policy. SHEET 139 places a fail-closed fleet synchronization barrier ahead of the existing authorization entry point. Every *configured required* custodian must durably install and sign an acknowledgement for the **same policy sequence, hash, and expiration** before a fleet receipt is issued.

There are **two deliberately distinct thresholds**:

- `2-of-3` operator signatures authorize *proposing* a SHEET 138 custody policy.
- `3-of-3` custodian acknowledgements are required to certify the *deployed* policy across this example three-node fleet.

A 2/3 witness quorum alone does **not** satisfy the new all-required synchronization barrier.

## New files

- `fleet139.js`: append-only, content-linked fleet history; Ed25519 acknowledgements; release receipts; explicit pending, quarantine, expiry, membership, and rollback conditions; crash-repair of missing node receipts from persisted signed policy.
- `host139.js`: local-only, real mTLS HTTPS witness process with `/policy` and `/ack` endpoints, pinned client certificate, and separate node signing keys.
- `bridge139.js`: composes the inherited `bridge138.authorize()` behind the verified fleet receipt, serialized with the same local coordination lock used by stage/ack operations.
- `gate139.js`: 65 tests including separate child-process witnesses, authenticated TLS, forged signatures, out-of-date nodes, hostile certificates, expired policy, tampering, rollback pins, quarantine, and crash windows.
- `run-all.sh`: runs 699 inherited checks in their isolated, preserved source tree followed by 65 new checks.
- `index.html`: interactive SVG precomputed scenario explorer. It does not control actual witness infrastructure.
- `KERNEL-ASCII.txt`: full architecture and policy state lattice.
- `SHA256SUMS`, `release-receipt.json`, `last-gate-report.json`: manifest and verifiable local test metadata.
- `baseline138/`: complete untouched SHEET 138 release. Inherited regression scripts create temporary test copies rather than changing this baseline.

## Quick start

Requires Node.js 22+, OpenSSL, Python 3, and Bash. Chrome or Chromium is optional for the UI smoke test.

```bash
cd sheet139
node gate139.js
bash run-all.sh
sha256sum -c SHA256SUMS
```

Node processes use ephemeral local test credentials and are shut down automatically after the test. No live production endpoint or persistent production private key is created.

## Policy barriers and failure examples

| Condition | Expected result |
|---|---|
| Signed policy staged; RED acknowledged | `PENDING_FLEET_ACK` |
| RED and BLUE acknowledged; GREEN unreachable | `PENDING_FLEET_ACK` |
| All three signed identical policy and expiry | `FLEET_VERIFIED` |
| Previously trusted GREEN returns and acknowledges exact policy | Recovery and certification |
| A custodian signs a different policy hash at same generation | Durable `QUARANTINE` |
| Missing/forged Ed25519 proof | `REJECT` |
| Expired policy | `HOLD` |
| Independently retained higher head pin | Local rollback rejected |
| Agent crashes after policy write but before ACK write | Reconstruct ACK from persisted signed policy |
| Contradictory membership | `HOLD` until deliberate reconfiguration process |

## Guarantees and limits

The local test verifies each ACK is cryptographically bound to the node identity, exact policy body hash, sequence, and expiry; and that all required node identities are represented exactly once. It also verifies the next authorization cannot run while a rollout is pending, the fleet is quarantined, or the policy is expired. Atomic filesystem rename and an explicit lock prevent cooperating local writers from racing.

**Not established:** independence across machines/operators, global distributed atomicity, hardware key storage, tamper-proof storage against an administrator controlling both evidence and keys, remote time synchronization, Byzantine consensus, and original SHEET 103 data parity. External head pins must remain in genuinely independent custody to detect a full-disk rollback. The all-required policy is a deliberate availability trade-off: a permanently offline node prevents new authorization until deliberate, explicitly audited membership change (not included in this release).

The bridge makes a *local* serialization promise, not a distributed global fencing promise. The rollout agents are real mTLS processes in tests, but all run on one machine. Out-of-band policy updates with valid operator signatures may reach individual nodes ahead of the fleet; no claim of instantaneous fleet-wide enforcement is made. Production authority remains disabled.

## Next target — SHEET 140

Auditable dynamic fleet membership changes with old/new joint consensus, expiring fencing leases, and independently operated multi-host witness deployment. Preserve the 139 regression baseline and never silently shrink the required custodian set.