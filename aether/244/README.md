# AETHER-244-RS — Signed source-ancestry challenge

An offline, fail-closed challenge adjudicator. Three receipts are checked against separately supplied Ed25519 public-key pins, one challenge/run binding, a previously consumed nonce snapshot, declared HTTPS allowlisted source URLs and bounded controller ancestry.

The production verifier uses cryptography's Ed25519 verifier. The 20 regression tests inject a mock signature verifier and therefore cannot establish a genuine external signature. Statements marked "externally pinned" still require **out-of-band authenticated** key enrollment.

The network policy is **declarative**, not measured enforcement. The tool never connects to the network. Real HTTPS acquisition needs an isolated runtime with private-network egress denial, DNS rebinding controls, redirect restrictions and an independently observed network policy. Source-controller labels and GitHub records do not prove separate ownership or custody.

Run:
```bash
python3 -m unittest discover -s aether/244 -p 'test_*.py' -v
python3 aether/244/challenge_gate.py --bundle authenticated-input.json --out hold-report.json
```

The command always exits 1 and returns REJECT_OR_UNVERIFIED; operational authority HOLD and physical qualification 0%. Phases XVIII and XIX remain frozen.

Next: AETHER-245-RS — isolate live HTTP acquisition from credential-bearing evidence evaluation, record actual egress enforcement and cryptographic challenge fixtures. Do not promote authority from synthetic witnesses.
