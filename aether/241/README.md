# AETHER-241-RS — Signed Cross-Controller Checkpoint Receipts

Bounded read-only receipt adjudication combining three expected Ed25519 signatures, separately supplied public-key pins, consistent run/checkpoint/challenge fields, replay ledger lookup and timestamp-order plausibility.

This module **does not establish trusted UTC**: `issued_at` and `checkpoint_at` are claims within signed statements. Even genuine signatures only establish that a key signed particular bytes. Controller labels are not independently authenticated controller ancestry. The nonces supplied in an input JSON list are not an immutable global replay registry.

Run:
```bash
python3 -m unittest discover -s aether/241 -p 'test_*.py' -v
python3 aether/241/receipts.py --bundle externally-acquired-snapshot.json --out hold-report.json
```

Tests use injected mock signature verification (NOT real cryptographic qualification). Production code calls OpenSSL to check Ed25519 signatures. All verdicts fail closed as `REJECT_OR_UNVERIFIED`. No physical ACT, lock reclamation, historical mutation, repair, or operational authority is granted. Phase XVIII and XIX freezes are unchanged.

Next natural bound: AETHER-242-RS — evidence of actual signing-key custody, trusted external timestamps and witnessed nonce consumption, keeping physical authority gated.
