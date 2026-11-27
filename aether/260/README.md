# AETHER-260-RS — Receipt Export & Offline Restart Replay

Produces a bounded snapshot from **one SQLite read transaction** containing the local CAS head, ordered accepted events and ordered attempt receipts. All rows are serialized to canonical JSON and joined with an export-wide SHA-256. The separate offline verifier recomputes receipt hashes, the event chain, the accepted attempt-to-event mapping, duplicate nonces/challenges, sequence monotonicity and final-head consistency.

Local tests create real SQLite records, re-export the ledger from a new connection, and mutate exported evidence to check missing, duplicated, reordered and substituted data. Canonical SHA-256 detects accidental or unauthorized changes **relative to a trusted earlier digest**, but a malicious custodian can rewrite the whole snapshot and its digest. This module does not implement external immutable custody or obtain independent witness attestations.

Run:

    python3 -m unittest discover -s aether/260 -p 'test_*.py' -v
    python3 aether/260/receipt_export.py export --db /tmp/aether258.db --out /tmp/aether260.json
    python3 aether/260/receipt_export.py review --input /tmp/aether260.json --out /tmp/aether260-hold.json

The collector only reads an existing local SQLite ledger; tests create temporary databases. No ACT. All reviews return REJECT_OR_UNVERIFIED and physical qualification 0%. Phase XVIII/XIX freezes remain untouched.

Next AETHER-261-RS: independently pinned export digests with three verified signature envelopes and cross-restart nonce replay rejection, without mislabeling local attestations as external custody.
