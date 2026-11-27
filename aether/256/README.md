# AETHER-256-RS — Externally Claimed Replay Ledger & Signer Ancestry

Fail-closed, read-only adjudication of multiple candidate append-only event histories anchored to a claimed external ledger head. It reconstructs SHA-256 event digests, verifies strict sequence and previous-head continuity, checks nonce replay against separately supplied history, detects conflicting history prefixes, and traces bounded graph ancestry for exactly three signer claims.

The source-controller graph and externally claimed head are **not authenticated merely by being included**. Three keys may have common ownership, and distinct ancestry labels may conceal that ownership. This version does not cryptographically validate the witness signatures (the prior AETHER-255 verifier handles signed witness statements). The ledger histories are snapshots and no atomic compare-and-swap or independently held immutable nonce consumption is executed.

Run:
    python3 -m unittest discover -s aether/256 -p 'test_*.py' -v
    python3 aether/256/replay_ancestry.py --bundle external-evidence.json --out hold-report.json

Every path returns REJECT_OR_UNVERIFIED, physical qualification 0%, operational authority HOLD. No earlier freezes are modified.

Next AETHER-257-RS: independently sealed external ledger compare-and-swap proof and controller-key lineage, with cross-host split-brain adversarial testing.
