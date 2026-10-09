# SHEET 146 — Remote Resource Fencing

SHEET 146 extends SHEET 145 with a crash-held, **resource-side** grant/receipt protocol. Three mTLS processes (authority, RED and BLUE resources) were tested on one machine.

## Key rule

An authority grants a resource write by durably recording exactly one pending transaction. A membership cutover cannot advance while that grant remains pending. A protected resource atomically persists its write, signs an Ed25519 receipt, and requests signed completion from the authority. If the resource crashes after writing but before completion, retry reconstructs the original receipt without repeating the write.

```
MOTHER KERNEL 145
  -> AUTHORITY / epoch + pending transaction
  -> mTLS signed grant
  -> RED or BLUE protected resource, independent persistence
  -> signed receipt
  -> authority completion / pending cleared
  -> membership cutover permitted
```

An Ed25519-signed independent rollback floor is retained in **separate local test storage**, checked against the authority's hash-linked journal. It is not a third-party external anchor.

## Verification

- 40/40 new regression tests passed.
- 1,017 inherited SHEET 145 tests passed **on rerun**; combined successful run 1,057/1,057.
- First combined attempt failed the known timing-sensitive SHEET 142 assertion (`2 !== 1`); do not treat the full chain as unconditionally deterministic.
- Chromium: eight scenario controls and JSON export passed.
- 378 inherited SHEET 145 files were verified byte-for-byte identical in the full release archive.

### Test limits

The system uses three real, local mTLS processes and synthetic credentials, *not* independently administered machines, consensus or production infrastructure. Direct-file writers could bypass the cooperating resource guard. The separately signed rollback floor is a local experimental control; external custody, hardware keys, cross-host linearizability, and SHEET 103 historical compatibility remain unverified.

The entire executable source, frozen SHEET 145 tree, release receipt and verification logs are in `SHEET146-remote-resource-fencing.zip` delivered with this release. The GitHub record here stores the release identity, architecture, and SHA-256 source digests.

```bash
cd sheet146
node gate146.js
bash run-all.sh
```
