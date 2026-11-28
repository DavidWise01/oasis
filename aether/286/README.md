# AETHER-286-RS — Atomic Complete Witness Manifest Retention

AETHER-285 found that AETHER-284 retained raw and observation hashes but omitted requested endpoint URLs, which are necessary to reproduce the exact acquisition batch hash. This fresh isolated journal stores the entire canonical manifest **in the same SQLite BEGIN IMMEDIATE transaction** as the three consumed witness nonces and SHA-256-linked batch head.

The manifest preserves the original canonical JSON signed claim bytes, complete original AETHER-264 observation fields (including raw base64 response bytes and requested URL), pinned trust-record digest, challenge nonce and previous batch head. Recovery recomputes SHA-256 from these original bytes, detects modifications to retained URLs, responses, observations or nonce associations, and checks historical externally supplied prefix sequence/hash. Duplicate challenge and witness nonces are rejected transactionally. The original AETHER-282 historical prefix is checked during capture through AETHER-283's signed claim verifier.

The verifier assumes caller-provided pinned keys and declared controller ancestry. Even genuine HTTPS acquisition from three endpoints does not demonstrate independently held signing keys, archived external custody, trusted time or whole-database anti-rollback. Local high-water prefix pins are not independent unless a separate trustworthy custodian actually preserves them. All results remain operational HOLD and physical qualification 0%.

Run tests:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/286 -p 'test_*.py' -v

Opt-in HTTPS capture:
    python3 aether/286/atomic_manifest.py capture --db /tmp/aether286.sqlite --journal /tmp/aether282.sqlite --trust pinned-trust.json --pin <64hex> --endpoints endpoints.json --challenge <fresh-nonce>

Replay:
    python3 aether/286/atomic_manifest.py audit --db /tmp/aether286.sqlite --prefix-seq 1 --prefix-sha <64hex>

Historical phase XVIII/XIX freezes and prior AETHER directories remain unmodified.

Next AETHER-287-RS: immutable external manifest export, separately preserved authenticated prefix receipts, crash/restart proof and ancestry review. Do not promote self-issued trust roots to independent authority.
