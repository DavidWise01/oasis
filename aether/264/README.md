# AETHER-264-RS — Bounded HTTPS Raw Evidence Acquisition

This phase adds a small HTTPS-only GET acquisition client that requires an explicit host allowlist, rejects credentials, fragments, IP-literal hosts, nonstandard ports, redirections, compressed response bodies, non-public DNS addresses (including link-local metadata targets), and oversize payloads. It pins the TCP connection to a validated DNS IP and uses normal TLS hostname verification against the original hostname. The body is recorded as base64 raw HTTP entity bytes with SHA-256 and metadata. It does not interpret body content as instructions.

A 200 or 206 response is accepted but not evidence of independent custody. TLS authentication is not controller ancestry or non-repudiation, and IP-based egress restrictions are not independently proven. This module does not follow redirects or perform external witness signing.

Run simulated regressions (no network):
    python3 -m unittest discover -s aether/264 -p 'test_*.py' -v

Explicit opt-in live HTTPS collection:
    python3 aether/264/acquisition.py --url https://example.org/evidence --allow-host example.org --out observation.json

The CLI exits nonzero on every path by design, and all analysis remains HOLD / 0% physical qualification. A live collection is **not** performed by the unit tests. Do not use an internal host or production endpoint in this diagnostic module.

Next AETHER-265-RS: independent HTTPS response retrieval from separate declared custodians, signed raw-body digests, stricter proof of transport provenance and cross-source nonce replay rejection.
