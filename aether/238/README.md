# AETHER-238-RS — Externally Pinned Receipt Gate

Read-only receipt-boundary work. The verifier checks Ed25519 signatures via OpenSSL, an out-of-band supplied trust-key map, challenge/run/pin bindings, nonce replay, and three distinct witness-root labels.

The trust roots **must** be acquired independently; do not treat a local JSON file created by the same workflow as an independent witness. Distinct witness-root labels do not establish separate controllers, original physical capture, or pre-run chronological authority. JSON timestamps are claims, not certified clocks. A mutable consumed-nonce ledger is only a local replay detector, not distributed replay protection.

All results are `REJECT_OR_UNVERIFIED` and physical ACT remains HOLD even when signatures validate. Tests use an injected mock verifier: they exercise decision logic only, not OpenSSL or hosted execution. To authenticate real statements, capture the public-key ancestry, signature bytes, challenge issuance, independently held receipts, and replay ledger from separate sources.

```bash
python3 -m unittest discover -s aether/238 -p 'test_*.py' -v
python3 aether/238/receipt_gate.py --receipts receipts.json --trust-roots externally-pinned-keys.json --consumed-nonces externally-held-ledger.json --out report.json
```

Earlier Phase XVIII/XIX freezes unchanged. No operational repair, physical ACT, history choice, or authority promotion.

Next bound AETHER-239-RS: independently checked key ancestry and sealed nonce consumption with adversarial controller-collusion tests.
