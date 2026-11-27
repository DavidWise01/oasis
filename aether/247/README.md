# AETHER-247-RS — Signed egress observation boundary

A standalone read-only verifier of claimed six-category denial measurements plus three Ed25519-signed observation statements. Local regression tests generate ephemeral Ed25519 keys, alter measurements and signatures, and confirm fail-closed behavior.

This verifier does **not** execute network probes. `namespace_separated` and `credential_free` are fields supplied by the caller, not independently measured facts. Signed observations verify that a key signed specific measurement bytes but cannot authenticate external controller custody, trusted chronology, or actual network enforcement.

```bash
python3 -m pip install 'cryptography>=43,<47'
python3 -m unittest discover -s aether/247 -p 'test_*.py' -v
python3 aether/247/egress_receipt.py --bundle externally-retained-evidence.json --out hold-report.json
```

All execution paths leave operational authority HOLD, physical qualification 0%. Phase XVIII/XIX freezes unchanged.

Next AETHER-248-RS: run a restricted egress probe under independently inspected network namespace and record independently signed raw probe transcripts; never promote from self-reported booleans.
