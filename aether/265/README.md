# AETHER-265-RS — Three-Source HTTPS Evidence & Signed Raw Receipts

An offline review boundary for three AETHER-264 raw HTTPS observations. It reconstructs exact body SHA-256 values, checks observation digests, validates public network peers and transport claims, binds each body and observation hash to one challenge and a distinct receipt nonce, and validates three genuine Ed25519 signatures using supplied public-key pins.

It also rejects repeated source labels, duplicate key IDs, duplicate hostname claims and shared ancestors in a supplied controller graph. The ancestry data and key pins remain caller-controlled and cannot independently prove distinct owners or service operators.

This phase does not issue live HTTPS requests. To obtain the observation inputs, use the separately developed AETHER-264 acquisition tool. No evidence of actual independent external retrieval is claimed here; a caller may construct the observations, the keys, and all three signatures.

Run offline:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/265 -p 'test_*.py' -v
    python3 aether/265/source_receipts.py --bundle combined.json --out hold.json

All reviews return REJECT_OR_UNVERIFIED and operational authority HOLD. Physical qualification remains 0%. Earlier Phase XVIII/XIX freeze files remain unchanged.

Next AETHER-266-RS: source acquisition receipt pinning to independently retained external challenge records and byte-level comparison across independent transport sessions, without promoting unverified custody.
