# AETHER-277-RS — Complete Rotation Ancestry and Restart Reconciliation

A read-only checkpoint auditor reconstructs the AETHER-276 signer registry from three original key/controller records, checks each ordered rotation with BOTH the retiring and incoming Ed25519 public keys, recomputes the exact intermediate registry digests and compares the full reconstructed head and rotation audit log with an existing AETHER-276 SQLite database.

An anchor statement binds the starting and expected registry digests, minimum challenge/receipt counts, completed rotation count and nonce. The caller supplies the canonical SHA-256 of that statement separately from the bundle. The audit refuses a missing anchored rotation, an old-key or new-key substitution, registry divergence after restart, history mismatch, count rollback, and a ledger where the number of stored receipts differs from three times the number of challenges.

**Boundary:** The anchor signature and public key are supplied with the bundle. This proves consistency only under that supplied key, not independent custody. A wholesale replacement of the database and all locally managed reference material could evade detection unless an external custodian actually retains the pinned digest and signing-key ancestry. This phase never grants operational ACT.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/277 -p 'test_*.py' -v
    python3 aether/277/recovery_audit.py --db /tmp/aether276.sqlite --bundle signed-rotation-history.json --trusted-anchor-sha256 <64hex> --out hold.json

No Phase XVIII/XIX or earlier AETHER directories are modified. Next AETHER-278-RS: independently retained checkpoint high-water records and multi-restart forensic replay comparison.
