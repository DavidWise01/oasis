# AETHER-253-RS — Externally Claimed Ledger Head and Process-Exit Boundary

The read-only adjudicator checks that ledger event sequences strictly advance from a caller-supplied previous head, checks SHA-256 event chaining and nonce repetition, binds an event to Linux process identity, and differentiates disappearance or PID reuse from a directly confirmed process exit.

Even if the evidence claims a pidfd wait or direct-child completion, this module does not perform a live process wait; the wait result remains a statement. A signed anchor is not externally authenticated merely because the input labels it so. Three Ed25519 signatures are checked cryptographically with temporary test keys, but that does not verify independence of the key controllers.

Run:

    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/253 -p 'test_*.py' -v
    python3 aether/253/exit_ledger.py --bundle evidence.json --out hold.json

Always REJECT_OR_UNVERIFIED; physical qualification 0%, operational authority HOLD. Does not signal, kill, reclaim a lock, or rewrite any past ledger. Phase XVIII/XIX freezes remain unmodified.

Next AETHER-254-RS: live Linux pidfd wait observation with a bounded independent supervisor and immutable digest-based process exit transcript, retaining the authority gate.
