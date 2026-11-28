# AETHER-288-RS — HTTPS Acknowledgment Acquisition & Durable Nonce Gate

AETHER-288 adds opt-in HTTPS acquisition to AETHER-287's locally signed export acknowledgment verifier. It uses the prior AETHER-264 bounded pinned-address HTTPS transport, verifies each raw response's exact body SHA-256 and canonical observation digest, requires the original acknowledgment JSON bytes to be canonical, and passes all three acknowledgments through AETHER-287's Ed25519, declared ancestry, and export-matching checks.

All accepted transport observations, raw response bytes (base64), source URLs, challenge nonce, trust digest, and SHA-256-linked acquisition batch head are committed to **one SQLite transaction** alongside all three consumed acknowledgment nonces. The read-only recovery audit checks canonical retained manifests, original raw bodies, nonce associations, batch-head hashes, and an optional pinned historical checkpoint.

Do not conflate HTTPS provenance, Ed25519 verification, or three distinct endpoint hostnames with three independent custodians. The public keys and ancestry claims still derive from the operator-supplied trust record. There is no external sealed nonce-history service; the entire local database may be replaced. The code does not fetch a separate externally preserved copy of the exported artifact or a real retention attestation. Every path remains operational HOLD, physical qualification 0%.

Run offline regression tests (mock transport, real ephemeral Ed25519):
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/288 -p 'test_*.py' -v

Opt-in live collection:
    python3 aether/288/ack_acquisition.py capture --db /tmp/aether288.sqlite --journal /tmp/aether286.sqlite --export export.json --trust trust.json --pin <64hex> --endpoints endpoints.json --challenge capture-nonce-longer-than-16
    python3 aether/288/ack_acquisition.py audit --db /tmp/aether288.sqlite --prefix-seq 1 --prefix-sha <64hex>

The capture command requires three explicitly mapped HTTPS endpoints and a pinned canonical trust-record SHA-256. Without authorized real endpoints, no live acquisition is attempted. Historical phase freezes are unmodified.

Next AETHER-289-RS: externally retained source-artifact readback and a durable, separately anchored acknowledgment high-water ledger, with explicit source ancestry rather than implied quorum.
