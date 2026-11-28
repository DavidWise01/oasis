# AETHER-273-RS — Externally Claimed Registry Anchor and Raw Transcript Readbacks

AETHER-273 compares a locally sealed AETHER-272 registry row set against a signed historical anchor statement supplied separately from an out-of-band SHA-256 pin. It checks registry row integrity and ordering, signer IDs, challenge count rollback, challenge replay history, exact raw bytes from three claimed sessions, matching body hashes for one immutable resource and three genuine Ed25519 signatures binding source identity, session, registry and challenge.

The out-of-band anchor is a **requirement imposed on the caller**, not an independently acquired or verified custodian record. This module performs no live network retrieval. Even completely valid signatures and a pinned digest cannot prove independent transport origins, ownership of signing keys, timestamp authority, or rollback-resistant external storage. All paths remain authority HOLD.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/273 -p 'test_*.py' -v
    python3 aether/273/external_anchor.py --bundle claimed-readbacks.json --trusted-anchor-sha256 <64hex> --out hold.json

No earlier phase files are altered. Next AETHER-274-RS: signed acquisition transcript provenance with verified external source records and explicit trust-chain acquisition, still refusing to infer independent custodians from three keys.
