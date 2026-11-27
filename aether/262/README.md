# AETHER-262-RS — Signed Nonce Checkpoint & Ancestry Gate

A read-only verifier for a previously retained checkpoint, one successor checkpoint, and up to 128 claimed nonce consumptions. It checks SHA-256 checkpoint linking, sequence/count monotonicity, per-nonce hash continuity, duplicate nonces, and three genuine Ed25519 signatures over both checkpoint digest claims. A bounded ancestry graph detects common controller ancestors behind distinct key identifiers.

The test suite generates ephemeral Ed25519 keys; no private key or real external evidence is committed. A caller can forge the checkpoint data, supplied public-key pins and ancestry graph together. Local integrity and cryptographic consistency do **not** independently establish external custody, verified signer independence, atomic nonce consumption, or physical ACT.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/262 -p 'test_*.py' -v
    python3 aether/262/checkpoint_gate.py --bundle checkpoint-bundle.json --out hold.json

The CLI is read-only and always exits nonzero, returning REJECT_OR_UNVERIFIED and operational HOLD with physical qualification 0%. Earlier Phase XVIII and XIX freezes are unchanged.

Next AETHER-263-RS: compare independently sourced checkpoint readbacks, cryptographically bind controller graph lineage, and reject external storage rollback without treating three claims as three independent witnesses.
