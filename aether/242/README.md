# AETHER-242-RS — External custody and time claims
Read-only validation of three claimed key custodians, three timestamp receipts, and three nonce-consumption receipts. It detects shared controller labels, altered receipt digests, mismatched binding fields, post-run timestamps, and repeated nonce values.

**Hard boundary:** records are untrusted snapshots. Their hashes do not establish cryptographic signatures or custody, and declared UTC strings do not authenticate time. An apparently valid triple cannot prove independent control. The tool therefore *always* emits REJECT_OR_UNVERIFIED, physical qualification 0%, operational authority HOLD.

Run:
```bash
python3 -m unittest discover -s aether/242 -p 'test_*.py' -v
python3 aether/242/custody.py --bundle independently-acquired-records.json --out review.json
```

Prior Phase XVIII and XIX freezes remain unchanged. No authority promotion, lock recovery, repair, or physical ACT. Next: AETHER-243-RS authenticated source retrieval and cross-source custody ancestry, followed by externally trusted clock qualification.
