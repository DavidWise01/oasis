# AETHER-292-RS — Provider Object-Version and Independent-Time Claims

This read-only qualification stage processes the two recovered AETHER-291 observation windows, six provider-signed object-version attestations (one per provider per window), and two clock-signed observation-time attestations. It verifies Ed25519 signatures against a separately pinned trust-record SHA-256, binds each object-version statement to the retained artifact digest, compares the provider's claimed object key/version across windows, binds each signed clock claim to the exact historical window head, rejects reused nonces, and detects overlapping declared controller ancestry.

Signed provider statements assert object_lock_mode (COMPLIANCE/GOVERNANCE), object_version, and a retention-until claim. These are protocol claims, NOT remotely independently verified provider API metadata. The timestamps are signed numbers; even strictly increasing timestamps do NOT prove an elapsed interval without independent clock custody and synchronization. A claimed controller graph and a trust-record SHA-256 supplied by one operator cannot prove independent witnesses.

The qualification loader first checks the AETHER-291 recovery audit for structural faults and refuses to process corrupt window chains. The new verification is read-only: old SQLite databases and historical phases remain unchanged.

Tests:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/292 -p 'test_*.py' -v

Read-only qualification:
    python3 aether/292/attestation_audit.py --db /tmp/aether291.sqlite --trust out-of-band-trust.json --trust-sha256 <64hex> --versions signed-provider-versions.json --times signed-time-witnesses.json --out qualification-HOLD.json

No real provider API, attestation service, or time source is queried by the tests. Operational authority remains HOLD and physical qualification 0%, even when every cryptographic check succeeds. Do not treat GitHub and 0root.ai mirrors as independent source custody.

Next natural bound AETHER-293-RS: provider-native authenticated read-only API response validation, vendor-issued version headers, and remote clock/time-chain evidence with externally established ownership. Authority HOLD until independent facts are observed.
