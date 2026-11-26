# AETHER-240-RS — Cross-witness checkpoint consistency

Phase XX. Read-only comparison of ledger checkpoints supplied by three or more claimed witness roots.

It checks event sequence, SHA-256 hash chaining, nonce uniqueness, run/challenge/source bindings, checkpoint identifiers, checkpoint length/head and **exact shared ledger prefixes**. Equal head hashes alone are insufficient. Internally consistent but divergent branches produce `DIVERGENT_LEDGER_HISTORY`.

Run locally:
```bash
python3 -m unittest discover -s aether/240 -p 'test_*.py' -v
python3 aether/240/checkpoints.py --bundle externally-acquired-bundle.json --out verdict.json
```

Locally authored fixtures cannot prove that witness roots are independent or that records were sealed outside GitHub. This implementation does not verify cryptographic signatures or secure timestamps. All verdicts remain `REJECT_OR_UNVERIFIED` with physical qualification 0% and operational authority HOLD. Earlier Phase XVIII/XIX freezes remain unmodified.

Next: AETHER-241-RS — externally sourced, independently verified checkpoint signatures and cross-controller custody receipts, without authority promotion.
