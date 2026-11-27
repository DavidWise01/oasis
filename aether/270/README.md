# AETHER-270-RS — Claimed Independent Anchor Readbacks & Rollback Evidence

This module consumes a previously pinned AETHER-269 nonce checkpoint together with three separately claimed checkpoint readbacks and signed acquisition statements. It verifies each AETHER-269 snapshot digest and original AETHER-268 nonce receipt, then detects nonce removals, substitutions, lower counts, conflicting same-count snapshots, duplicate signer IDs, replayed readback nonces and declared shared controller ancestry. The Ed25519 signatures are cryptographically verified against pins supplied by the caller.

This is not independent acquisition: no live network reads occur here, and the supplied retrieval digest is not a separately observed byte stream. The caller also supplies public keys, the original anchor, and controller ancestry. Their honesty and independent ownership are unproven. Three valid local signatures are NOT an external quorum or a basis for physical ACT.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/270 -p 'test_*.py' -v
    python3 aether/270/anchor_readback.py --bundle claimed-anchor-readbacks.json --out hold.json

All verdicts stay REJECT_OR_UNVERIFIED, operational authority HOLD, physical qualification 0%. No frozen earlier phase files are modified.

Next AETHER-271-RS: direct raw-response acquisition receipts and independent pin-owner authentication with explicit provenance/ancestry limitations.
