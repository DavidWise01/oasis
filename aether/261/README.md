# AETHER-261-RS — Signed Export Continuity and Replay Gate

This read-only verifier receives two AETHER-260 ledger exports, a fresh challenge, an externally *claimed* nonce/digest history, and three Ed25519 signature envelopes. It checks export self-hashes and event-prefix continuity, binds both export SHA-256 values to run/source/host/challenge, and rejects claimed replayed challenge, witness nonces and export digests. Signatures are checked against caller-provided key pins, but their origin is not independently authenticated.

The test suite uses real ephemeral Ed25519 private keys and temporary SQLite files; no signing secrets are committed. It cannot prove key custody, external ledger atomicity, or which real machines observed the records. This is deliberately HOLD even with three locally verified signatures.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/261 -p 'test_*.py' -v
    python3 aether/261/signed_exports.py --bundle ledger-bundle.json --out hold.json

All paths remain REJECT_OR_UNVERIFIED, physical qualification 0%, operational authority HOLD. Historical Phase XVIII and XIX freezes remain untouched.

Next AETHER-262-RS: validate a separately persisted, cryptographically authenticated nonce-ledger checkpoint across restarts and reject forged ancestry or duplicate purported witnesses.
