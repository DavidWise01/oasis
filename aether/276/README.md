# AETHER-276-RS — Durable Signed Receipts & Two-Sided Key Rotation

This phase provides a local SQLite signer registry, persistent challenge/session replay fence, and explicit Ed25519 key-rotation authorization. Registry initialization requires three entries and a separately supplied canonical SHA-256. Signed three-source receipt bundles are committed in a single BEGIN IMMEDIATE transaction. Any invalid signature, stale registry pin, reused nonce, or duplicate source rejects the entire transaction.

Key rotation requires both the incumbent private key to sign its exact replacement statement and the incoming private key to prove possession by signing the same statement. The statement binds source, controller, previous registry SHA-256, old/new PEM digests, and next version. Rotation updates the registry and retains an audit record atomically.

Local SQLite retention is not tamper-resistant external storage; a disk image can be rolled back, the bootstrap pin can be self-issued, and three registered signer labels can share one custodian. This module does not collect live HTTPS responses or independently authenticate owner ancestry. All results are HOLD and physical qualification 0%.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/276 -p 'test_*.py' -v
    python3 aether/276/durable_receipts.py bootstrap --db /tmp/aether276.sqlite --keys signer-entries.json --pin <64hex>
    python3 aether/276/durable_receipts.py consume --db /tmp/aether276.sqlite --bundle signed-receipts.json --pin <current64hex>
    python3 aether/276/durable_receipts.py inspect --db /tmp/aether276.sqlite

The CLI also supports rotate with both signatures and a pinned incumbent registry digest. Use scratch data. Earlier frozen phases are unchanged.

Next AETHER-277-RS: independently verified key-rotation ancestry, externally anchored head digest and crash/restart reconciliation, without granting operational authority.
