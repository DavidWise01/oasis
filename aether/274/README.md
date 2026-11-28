# AETHER-274-RS — Acquisition Provenance, Raw Bytes and Pinned Source Identity

This read-only verifier consumes three AETHER-264-shaped HTTPS observations and three Ed25519 acquisition receipts. It compares exact base64 response-body bytes, raw SHA-256 and observation record SHA-256, the pinned immutable resource URL, a pinned source hostname, and a challenge expected digest. It verifies each signature over session, source, challenge, and raw observation digest.

An out-of-band canonical SHA-256 of a source registry must be provided separately. Registry entries declare key IDs, public keys, hostnames, controllers, and ancestry. The verifier flags self-issued or shared controller ancestry in these declarations; the graph itself is not independently authenticated. Reused challenge and session nonces, duplicated source/session/key IDs, substituted raw data, unsafe recorded peers, and conflicting body digests are rejected as inconsistencies.

Importantly, the verifier does **not** perform HTTPS requests; all observations remain caller supplied and can be fabricated coherently. Unlike live acquisition evidence, a correctly signed observation with a pinned key proves only that the supplied key signed the statement. It does not establish separately operated sources, transport-session independence, external custody, timestamps, or authority to ACT.

Run offline:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/274 -p 'test_*.py' -v
    python3 aether/274/provenance_gate.py --bundle observations.json --trusted-registry-sha256 <64hex> --out hold.json

Historical Phase XVIII/XIX freezes are unchanged. Every result retains operational authority HOLD and physical qualification 0%.

Next natural bound AETHER-275-RS: authenticated external key-ring acquisition, independent live transcript capture and receipt replay against independently preserved challenge evidence.
