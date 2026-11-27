# AETHER-271-RS — Raw Checkpoint Readbacks & Out-of-Band Trust Pin

This phase cross-checks three supplied raw (base64) checkpoint readbacks against an AETHER-269 snapshot. It recomputes the exact raw-body SHA-256, parses and verifies the embedded checkpoint and nonce receipt hashes, and checks Ed25519 readback signatures against a trust record whose canonical SHA-256 must be passed separately via --trusted-pin-sha256.

The additional command-line pin prevents a silently rewritten bundle from changing its own trust record **unless the operator also changes the separately provided digest**. It is not a source of externally authenticated ownership. The trust record contains purported signer owners and a controller graph; explicit ancestry checks reject shared and self-issued origins as declared. No real HTTPS requests are performed in this module.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/271 -p 'test_*.py' -v
    python3 aether/271/raw_pin_owner.py --bundle captured-readbacks.json --trusted-pin-sha256 <trusted 64hex> --out hold.json

Use independently established pin provenance before drawing ownership conclusions. All reports are REJECT_OR_UNVERIFIED, operational authority HOLD and physical qualification 0%. Historical phase freezes remain untouched.

Next AETHER-272-RS: transport acquisition transcripts bound to an independently maintained trust registry and challenge history with signed receipt readback comparisons.
