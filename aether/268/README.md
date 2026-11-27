# AETHER-268-RS — Byte-Pinned Issuance Readback & Persistent Nonce Fence

A read-only pin checker validates separately provided raw issuance response bytes against an expected SHA-256 and a declared challenge pin, rejecting URL substitution, body replacement, length mismatches and pin corruption. The checked observation itself is supplied by the caller; no independent HTTPS retrieval is performed by this module.

A separate, local SQLite nonce ledger provides a real atomic UNIQUE nonce constraint across process restarts. Transactions use BEGIN IMMEDIATE with WAL and synchronous=FULL, and store deterministic SHA-256 receipts. Reusing a committed nonce is rejected regardless of its new claimed challenge.

This is local persistence, not an independent external nonce authority, tamper-proof append-only storage or proof of independent issuance custody. The module does not authenticate pin-owner identity or witness ancestry. All commands return operational HOLD and 0% physical qualification.

Commands:

    python3 -m unittest discover -s aether/268 -p 'test_*.py' -v
    python3 aether/268/issuance_pin.py check-pin --input pinned-readback.json
    python3 aether/268/issuance_pin.py consume --db /tmp/aether268-nonces.db --nonce example-1 --challenge-sha256 <64hex> --issuance-sha256 <64hex>
    python3 aether/268/issuance_pin.py inspect --db /tmp/aether268-nonces.db

Use a scratch database; consume mutates the specified file. Historical freezes remain unchanged.

Next AETHER-269-RS: externally authenticated monotonic nonce checkpoints and cross-run rollback comparisons using independently pinned public keys; continue to reject self-signed source ancestry.
