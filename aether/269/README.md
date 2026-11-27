# AETHER-269-RS — Signed Monotonic Nonce Snapshots

This phase reads real AETHER-268 SQLite nonce receipts into a bounded sorted snapshot, then checks recovery evidence against a supplied **signed prior snapshot**. The verifier computes canonical SHA-256 over each snapshot, validates receipt hashes, verifies an Ed25519 anchor signature against a separately supplied public-key pin, and rejects removal or replacement of an anchored nonce. A new nonce may sort anywhere in the snapshot, so prefix-only comparisons are inappropriate; membership and record equality are checked instead.

Local SQLite commits can be rolled back by replacing the entire database with older bytes. The presence of a previous signed checkpoint *within the same caller-controlled evidence bundle* is not external anchoring. The verifier is always HOLD even when all cryptographic checks succeed. An independent custodian must retain the pinned digest and authenticated key ancestry before external anti-rollback claims are justified.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/269 -p 'test_*.py' -v
    python3 aether/269/checkpoint_anchor.py snapshot --db /tmp/aether268-nonces.db --out snapshot.json
    python3 aether/269/checkpoint_anchor.py review --bundle claimed-bundle.json --out hold.json

The snapshot command is read-only. No signing keys, external custody credentials, operational ACT or modifications to earlier frozen phases.

Next AETHER-270-RS: independently acquired checkpoint anchors, authenticated pin ownership, and cross-origin rollback evidence without conflating duplicate source ancestry with quorum.
