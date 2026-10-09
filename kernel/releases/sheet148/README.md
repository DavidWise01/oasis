# SHEET 148 — Replicated Authority to Protected Resource

**Status:** `0e / PASS`, **46/46 new regression checks**. The complete inherited SHEET 147 lineage is copied unchanged into `baseline147/`; its nominal 1,068 checks are run in a separately copied temporary tree. This is a local, synthetic multi-process build, not production certification.

## Purpose

SHEET 147 introduced quorum-certified authority journal commits but preserved the SHEET 146 resources without connecting them to the new quorum. SHEET 148 bridges that last mile using real local mTLS processes, signed prepare and state attestations, a resource-side live majority check, and idempotent durable resource receipts.

## Modules

- `bridge148.js`: checks the current epoch before BEGIN, creates a quorum-certified grant, verifies resource Ed25519 receipts, completes at the replicated authority, and honors leader-term changes.
- `proof148.js`: checks distinct Ed25519-signed replica prepare votes and state signatures; verifies exact transaction digest, resource, epoch, committed log hash, and active pending grant.
- `resource148.js`: pinned mTLS endpoint; verifies grant, checks live quorum twice around optional delay, persists hash-linked resource records atomically, signs deterministic receipts, and reuses a durable receipt after crash without replaying the write. Can check an independently retained, signed local rollback floor.
- `gate148.js`: ephemeral development keys, openssl CA, three independent replica processes plus one resource process, 46 adversarial checks including a real resource crash, term handoff, partition loss, recovery, wrong pins, forged signatures, and rollback-floor attacks.
- `baseline147/`: immutable copy of all SHEET 147 files, including its complete predecessor lineage.

## Run

Requires Node.js 22+, OpenSSL, Bash, loopback sockets.

```bash
cd sheet148
node gate148.js
bash run-all.sh
```

The inherited runner is executed inside a disposable copy of `baseline147`, so older logs and manifests are not overwritten. The new test fixture generates short-lived development keypairs and removes them afterward.

## Transaction lifecycle

1. `bridge.begin()` validates current epoch and obtains 2/3 replica prepare signatures followed by 2/3 committed state attestation for a `BEGIN` grant.
2. The resource rejects forged proofs and queries 2/3 current replica states over mTLS before the first physical write. The grant prevents `CUTOVER` until completion.
3. The resource atomically persists one hash-linked record and creates an Ed25519-signed receipt. If the worker dies, it returns that identical receipt after restart.
4. `bridge.complete()` independently checks the resource signature and matching pending grant and obtains quorum certification of `COMPLETE`.
5. Only then may `CUTOVER` advance. A new leader can complete a retained grant, and old elected-term leaders cannot certify a new operation.

## Important limitations

**Security limitation requiring the next sheet:** the inherited SHEET 147 `/commit` implementation accepts a majority-certified `COMPLETE` proposal containing a receipt *hash* rather than verifying a resource-signed receipt in the replica itself. SHEET 148's bridge validates the receipt, but a compromised or bypassing elected leader could submit a hash directly to the replica API. Therefore **resource-authorization correctness against malicious authority leaders is not yet established**. Closing this replica-enforced receipt-verification gap is the most urgent SHEET 149 target.

Further limits: the three replicas and protected resource run as distinct mTLS processes **on the same physical host**; the independent rollback floor is a separate local directory, not externally operated custody. The tests do not establish global linearizability under arbitrary schedules. The inherited SHEET 142 timed concurrency assertion has failed intermittently in earlier releases and has not been fixed by SHEET 148. Original historical SHEET 103 fixture parity remains unverified.

No keys in this release should be used in production. No GitHub upload or HTML scenario widget constitutes a live production deployment.