# SHEET 158 — Bounded-Page Witness Recovery with Signed Consistency Links

**Status:** dedicated new gate `58/58 PASS` (Node.js 22, three mTLS witness processes). The inherited chain is separately recorded in `combined-run.log` and `combined-exit.txt` when available.

## What changed

- The SHEET 157 recovery path transferred an entire signed history and capped proofs at 256 records. SHEET 158 adds **signed page exports (1–24 records)**, certifies an exact high-water target with two independent Ed25519-signed witness heads, and imports only the missing suffix.
- The target retains the hash-linked local prefix, pending signed promise, fresh nonce, target certificate, certified source identities, and verified page cursor in an atomic, crash-recoverable local record.
- Every page binds `nonce + targetSlot + targetHead + cursor + prevHead + next + endHead + recordsDigest`, and is signed by a certified exporter. Records must be canonical and uninterrupted. A bad, missing or repeated page never silently advances the cursor.
- After a real process crash between a durable page and RPC reply, the coordinator reads signed `/status158` and resumes at the *already persisted cursor*, rather than retransferring the old page.
- Normal witness `/prepare` and `/commit` fail closed during an active recovery session. A conflicting prepared vote is quarantined; a successful recovery clears a matching promise only after all pages and the target head verify.
- The original SHEET 157 API, source, and all earlier lineage remain frozen under `baseline157/`.

## Run

```bash
node gate158.js         # new fault tests only
bash run-all.sh         # inherited frozen lineage, then new tests
```

Dependencies: Node.js 22+, OpenSSL CLI for test certificates, Bash, Python 3 for archive tooling. Tests allocate loopback TLS ports and temporary identities; no remote services or production secrets are required.

## Modules

- `page-verify158.js` — quorum head certification, canonical page-link verification, bounded page creation, pending-promise checks.
- `witness158.js` — S157 witness with additive `/begin158`, `/page158`, `/status158`, `/apply158`, `/finish158` endpoints, atomic recovery state, and old-operation admission holds.
- `catchup158.js` — client-side mTLS transport, minority quorum discovery, page selection, resume following lost replies, signed final receipt.
- `gate158.js` — three TLS witness services, 337 seeded genesis-consistent records, live 338/339 grants, signed malicious page injection, process restarts and kill-after-fsync recovery.
- `index.html` — interactive emerald fault viewer; `KERNEL-ASCII.txt` — full process pipeline.

## Test provenance

The 337-record majority history is a **synthetic but fully hash-checked fixture**, *not 337 independent real quorum transactions*. Slots 338 and 339 use actual signed prepare/commit RPCs over loopback mTLS. The newly added repair passes >256 total history records; each message contains at most 24 records.

## Security and scalability limits

The 2/3 signed target checkpoint is constant in size and each authenticated page is bounded. **This is a compact page-link consistency scheme, not an O(log n) Merkle consistency proof**; transferring the complete missing suffix still costs O(n) data. The target stores history plus staged recovery pages in one JSON state file and revalidates its history on access, which can scale poorly. This release does not implement independent physical hosts, a Byzantine consensus protocol, external rollback pins for a wholly restored disk image, online key rotation, or atomic cross-host storage. A malicious majority can certify a false history. The older SHEET 142 timing-sensitive test remains unproven resolved.

## Verification

`release-receipt.json` records the latest independently observed result. `SHA256SUMS` covers every included release file excluding the manifest itself; the full ZIP contains the entire byte-identical SHEET 157 release tree. ZIP SHA-256 is in the adjacent `.sha256.txt` file.