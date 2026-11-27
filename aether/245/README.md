# AETHER-245-RS — Isolated acquisition boundary and real Ed25519 fixtures

Read-only offline qualification of previously acquired bytes. The verifier does not make network requests, use GitHub tokens, mutate evidence or promote operational authority.

For each of three envelopes, reconstruct SHA-256 of downloaded bytes, check signed challenge/run/source fields, detect replayed nonces and duplicate bytes, and verify Ed25519 statements with the `cryptography` library. Tests generate ephemeral private keys locally; no private keys or user credentials are committed.

A successful signature verification proves only possession of the corresponding private key. Self-supplied key pins are not independently authenticated key custody. The claimed isolation of an acquirer is **not** verified by this module; actual network isolation requires separately observed runtime enforcement and external checks.

```bash
python3 -m pip install cryptography
python3 -m unittest discover -s aether/245 -p 'test_*.py' -v
python3 aether/245/qualification.py --snapshot independently-collected-snapshot.json --out hold-report.json
```

All results remain `REJECT_OR_UNVERIFIED` and operational authority HOLD, physical qualification 0%. Earlier phases remain frozen. The local development prototype passed 18 tests after fixing an invalid-signature exception path. GitHub Actions execution must be checked independently.

Next AETHER-246: externally measured egress isolation with a credential-free acquisition process and evidence receipts pinned by an external controller.
