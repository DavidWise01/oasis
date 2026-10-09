# SHEET 141 — Protected-Resource Fencing

**Status:** `0e / PASS` — 36 new local regression checks, 827 inherited SHEET 140 checks: **863/863 checks** in the release runner. Test-only infrastructure, not a production authorization certification.

## Goal

SHEET 140 issued monotonic membership fencing leases but enforced them only at the Mother Kernel callback. SHEET 141 introduces two separately running protected-resource processes. Every write must authenticate its TLS client, consult a *pinned* online membership authority, independently verify a short-lived Ed25519 authority checkpoint, validate the client's inherited SHEET 140 lease, check the resource's persisted highest-seen epoch/fence, and only then append a durable SHA-256-linked write.

## Architecture

- `fencing141.js`: resource-side authority verification, checkpoint freshness, inherited `membership140.validateLease()` enforcement, durable receipt ledger and cross-process lock.
- `authority141.js`: separate mTLS HTTPS membership checkpoint service; validates SHEET 140 stable membership and SHEET 139 signed fleet on each request, then signs a short-lived checkpoint using an independent Ed25519 identity.
- `resource141.js`: separate mTLS protected resource process; client must possess a CA-authorized certificate and valid lease. Performs two membership authority reads in its critical section, including a refresh immediately before the durable write. This is a *best effort fail-closed guard* rather than formally linearizable distributed transactions.
- `gate141.js`: 36 checks using a real inherited signed fleet and genuine SHEET 140 joint membership cutover, two TLS resources, genuine certificate pinning and process restarts, forged leases, forked/tampered state, concurrency, delay, and partition failures.
- `baseline140/`: unchanged complete SHEET 140 dependency with all frozen earlier releases.
- `index.html`: interactive **precomputed fault scenario** SVG. It is not a remote control system.
- `KERNEL-ASCII.txt`: compact full overlay of the new execution boundary.
- `run-all.sh`: runs inherited suites from a throwaway copy and then SHEET 141 gate.

## Run

```bash
cd sheet141
node gate141.js
bash run-all.sh
sha256sum -c SHA256SUMS
```

Requires Node.js 22+, OpenSSL, Python 3 and Bash. All TLS certificates and signing keys used in tests are ephemeral and stored under a temporary directory that the test runner deletes. No production credentials are included.

## Safety properties demonstrated

- A writer with a valid SHEET 140 lease for epoch 1 cannot write after the online authority advertises committed epoch 2.
- A delay between early verification and the final check causes an old in-flight writer to be rejected if cutover occurs during that delay.
- A protected resource refuses mutations when its pinned membership authority cannot be contacted or signatures do not validate.
- Each protected resource maintains its own monotonically observed fence and durable operation ledger across process restarts.
- Duplicate operation IDs do not create duplicate writes, and conflicting reuses are rejected.
- The certified old member remains required to approve the joint transition under the inherited SHEET 140 rules; this release does not invent a break-glass bypass.

## Limits — not proven

1. **Not globally linearizable fencing.** An authority transition can race after the final authority read but before a resource completes a durable write. Full correctness requires a shared linearization point or a lease/fencing protocol that atomically orders authority cutovers and resource mutations. This is the next research target.
2. These are **three processes on one machine** over real local mTLS, not independent remote hosts.
3. A resource's entire local history could be rolled back along with its local file unless the high-water pin is retained elsewhere.
4. Each service certificate is signed by a local test CA; certificates have no production custody or attestation.
5. The resource trusts any valid writer client certificate from its configured test CA, but still requires a valid membership-signed lease. Production should bind writer certificates to specific roles/identities.
6. Distributed consensus and liveness under arbitrary host crashes, byzantine faults, and unbounded clock skew remain outside this test.
7. Historical SHEET 103 parity remains unverified.

## Next target

SHEET 142: move the authority and resource write path to an explicitly serialized commit protocol with durable external fence pins, rather than relying on two checkpoint reads.