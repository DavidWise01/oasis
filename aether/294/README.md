# AETHER-294-RS — Opt-in HTTPS Provider and Clock Evidence Capture

AETHER-294 introduces a bounded public HTTPS GET collector using the AETHER-264 transport. An operator supplies a *separately pinned*, canonical acquisition plan with three provider endpoints and one clock endpoint, each queried once for each of two declared observation windows. This captures eight unmodified response bodies and full AETHER-264 transport observations in a single SQLite commit. The recovery audit re-hashes retained bodies and their transport observations, the batch's canonical manifest, and its eight observation indexes. Changes are rejected; historical phases are not modified.

Source checks: only HTTPS on port 443, no redirect acceptance, bounded public DNS and pinned resolved IP, TLS hostname validation, 64-KiB response limit, canonical JSON payloads, consistent source hosts across windows, no duplicated source host, stable claimed object key/version per provider, unchanged artifact SHA-256, unique source nonces, and a forward-linked pair of clock claims.

## Evidence qualification limits

AETHER-264 is a GET-only, public HTTPS reader. It **cannot** query private AWS/Azure/GCP object-lock APIs requiring authenticated cloud credentials or establish the storage account's actual identity. This phase intentionally does not pretend that its JSON payloads were issued by a storage vendor, or that HTTP header fields are vendor signatures. It retains evidence that a TLS endpoint returned the bytes, not independent origin, immutability or identity. It does not independently verify Ed25519 signatures on clock body claims: those are carried as untrusted retained bytes for later qualification. Two GETs in one CLI invocation do not establish independent elapsed time.

The existing AETHER-293 offline qualification remains separate. Do not promote an operator-pinned plan, distinct hosts, repeated requests, or claimed object-lock metadata into external custody proof. Neither GitHub nor 0root.ai is an independent witness to itself. Operational authority stays HOLD, physical qualification 0%.

Run:
    python3 -m unittest discover -s aether/294 -p 'test_*.py' -v

Explicit live capture:
    python3 aether/294/live_provider_capture.py capture --db /tmp/aether294.sqlite --plan acquisition-plan.json --plan-sha256 <sha256> --nonce fresh-capture-nonce-294

Offline readback:
    python3 aether/294/live_provider_capture.py audit --db /tmp/aether294.sqlite

Tests use mocked transport only. No live provider or clock service was contacted by authoring or CI wiring.

Next AETHER-295-RS: actual provider-specific authenticated API connector or approved credential mechanism, exact HTTP/header capture including version and retention metadata, independently verified time source, and read-only signature binding without implying external custody.
