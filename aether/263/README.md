# AETHER-263-RS — Readback Comparison & Claimed Rollback Evidence

This offline read-only verifier checks three separately labelled checkpoint readbacks, each with a bounded history and Ed25519 signature. It recomputes checkpoint SHA-256, checks checkpoint ancestry and monotonic sequence, recognizes claimed stale heads or a fork at the anchor, and detects shared nodes in a supplied controller ancestry graph.

The three readbacks are supplied by one caller; this phase **does not collect evidence from three independent services**. A caller can fabricate the checkpoint, keys, graph, and history consistently. Three signatures and three labels are not proof of three independent origins. The verifier always keeps physical qualification 0% and ACT on HOLD.

Run:

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/263 -p 'test_*.py' -v
    python3 aether/263/checkpoint_readback.py --bundle evidence.json --out hold.json

Source files and CI are new; Phase XVIII and XIX freezes remain unchanged.

Next AETHER-264-RS: an evidence-acquisition adapter that records exact external response bytes and retrieval provenance separately from self-asserted custody labels, with signed pinning and replay protection.
