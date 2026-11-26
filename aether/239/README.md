# AETHER-239-RS — Controller Ancestry and Sealed Nonce Review

This module checks an *untrusted snapshot*: witness key-to-controller ancestry (including shared ancestors and cycles), and a deterministic append-only nonce ledger chain with exact sequence numbers, nonce uniqueness, event hashes, and an externally supplied head digest.

The ledger is read-only. No event is consumed or appended. The supplied `externally_pinned_head` is only a claim unless retained and authenticated outside the evaluated system. Different keys and labels do not prove independent controllers; a chain hash does not make storage immutable. No real external custody or physical witness is claimed.

Run:
```bash
python3 -m unittest discover -s aether/239 -p 'test_*.py' -v
python3 aether/239/controller_ledger.py --input externally-acquired-snapshot.json --out hold-assessment.json
```

The assessment always retains physical qualification 0%, physical ACT disallowed, and operational authority HOLD. Phase XVIII and XIX freezes are unchanged.

Next: AETHER-240-RS, externally witnessed append-only ledger consistency with signed pre-run checkpoints and byzantine-source ancestry controls.
