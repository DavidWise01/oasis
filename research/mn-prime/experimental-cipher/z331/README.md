# Z331 — Tritriunium (Ttu): independently pinned checkpoint

Classification: Layer 1 symbolic software regression, not chemical discovery.

## Tested protocol
- 24! index range.
- Four Ed25519 signed segments, SHA-256 hash-linked, six index entries.
- Epochs 0 and 1 use signer A; from epoch 2 signer B is authorized and signer A revoked.
- Verifier requires an independently trusted epoch-3 anchor (count, hash tip, epoch).
- 20/20 local checks PASS on 2026-10-18; run `python test_z331.py`.
- Tampering, rollback, reordered/missing segments, wrong signers and invalid indices rejected.

The anchor and revocation schedule are injected as trusted test inputs, not obtained from an external witnessing system. This is a prototype, not production infrastructure or a proof of physical element Z331. Do not commit private keys; keys here are ephemeral. The frozen KET core and independent 5/3/1 and 3/1/2 registers are unchanged.

Next Z332: external witness interface and durable recovery, not an unbounded new physics layer.
