# AETHER-267-RS — Challenge Issuance and Ancestry HOLD

A read-only cryptographic gate binds one separately declared challenge issuance receipt to three transport receipts. It verifies a genuine Ed25519 issuance signature, three transport signatures, challenge and body digest agreement, and nonce replay checks. It walks the declared controller graph to reject an issuer whose ancestors overlap any transport controller, and detects shared ancestry among transport receipts.

This phase does not perform network acquisition or authenticate where the issuer's private key resides. All pins, history and ancestry are caller-supplied, so matching signatures and disjoint graph labels cannot prove that external custody or truly independent witnesses exist. Earlier AETHER-264/266 are separate raw-byte and transport-session layers.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/267 -p 'test_*.py' -v
    python3 aether/267/challenge_provenance.py --bundle claimed-bundle.json --out hold.json

All outputs are REJECT_OR_UNVERIFIED, operational authority HOLD and physical qualification 0%. Earlier phase freezes remain unchanged.

Next AETHER-268-RS: independently retrieved issuance-pin bytes with source-specific cryptographic anchors and nonce persistence, without treating self-supplied evidence as independent.
