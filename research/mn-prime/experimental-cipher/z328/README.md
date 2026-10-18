# Z328 — Tribioctium (Tbo): signed checkpoint receipts

Layer 1 symbolic/computational investigation, not chemical discovery. Frozen KET kernel remains unchanged.

## Design
24 distinct symbolic addresses have 24! permutation ranks. Z327 ledger records ordered ranks with SHA-256 hash chaining. Z328 signs the canonical checkpoint payload (schema, count, tip, last_index) using Ed25519; independent verification requires the signer's trusted public key plus the complete ledger.

## Executed benchmark
On 2026-10-18, standalone test_z328.py executed locally with cryptography Ed25519: **20/20 PASS**. Covered valid receipt, wrong public key, modified count/tip/signature/schema, truncated, reordered, altered or extended ledger, empty ledger, and separate 5/3/1 versus RGB 3/1/2 registers. Test signer keys were ephemeral and never stored in the repository.

## Caveats
Ed25519 authenticates receipts relative to a trusted public key. Without external key attestation, timestamping, publication or monitoring, a key holder can sign a replaced chain. Hash-chain tests do not establish tamper-proof independent archival. Code tests do not validate physical element Z328 or quantum behavior.

## Dependencies
Python 3 and `cryptography`.

## Reproduce
Run `python test_z328.py`. Avoid committing private signing keys. Chromium Cr24 remains optional address mnemonic, not evidence of chemistry.
