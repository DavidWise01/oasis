# AETHER-293-RS — Preserved Provider Response Bytes & Signed Time Chain

This phase validates six exact provider-response JSON preimages (three provider objects for each of the two AETHER-291 observation windows) and a two-link Ed25519-signed time chain. Each provider record must preserve raw response base64, SHA-256, a claimed HTTPS request/response ID, object key, immutable version ID, object lock mode, retention date claim and content digest. Clock statements bind the claimed time to the exact AETHER-291 window head and to the previous signed statement.

It rejects response substitution, missing or duplicated provider/window pairs, changed version IDs, invalid transport-observation claims, broken time chains, nonmonotonic clock claims, overlapping declared operator ancestry and mismatched pinned trust-record hashes.

**Critical limitations:** These are caller-supplied response records, not actual storage-provider API authentication. The claimed TLS peer flag is not independently verified by this offline qualification step. A response body digest does not prove the provider issued the response; no vendor signature or verified service identity is assumed. Likewise, a signature from a caller-pinned clock key proves only possession of that key, not clock accuracy, independently elapsed time or independent operator identity. All outputs remain HOLD, physical qualification 0%. The existing AETHER-291 journal and earlier phase freezes are read-only and unchanged.

Tests:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/293 -p 'test_*.py' -v

Read-only qualification:
    python3 aether/293/provider_native_audit.py --journal /tmp/aether291.sqlite --trust pinned-roots.json --pin <SHA-256> --responses preserved-provider-responses.json --clock-chain signed-time-chain.json --out qualification-hold.json

Next AETHER-294-RS: live, opt-in storage-provider API response capture with strict service-domain allowlists, native response-byte custody, version-ID continuity and separately authenticated clock-source acquisition. Do not imply provider identity from self-declared JSON.
