# AETHER-266-RS — Externally Claimed Challenge Pin & Three-Session Readback

This read-only verifier compares three claimed, independently acquired AETHER-264 HTTPS observations of the **same canonical resource** against a declared challenge pin. It reconstructs each raw base64 body SHA-256, checks the challenge pin's digest, verifies each session's Ed25519 signature, and rejects replayed nonces, duplicated session IDs, unsafe peers, source-URL substitution and conflicting body hashes.

Three different URLs serving different content should not be compared for byte equality. This phase deliberately requires the same resource URL and expected exact body digest across three sessions. Non-identical responses cause HOLD; this may be expected for dynamic resources and must not be misconstrued as malicious behavior.

The alleged external pin, public keys, nonce ledger and three session identities come from the input bundle. Their independently observed provenance is **not** established by this program. Even a clean local test and three correct signatures cannot establish remote custodian independence, external timestamp authority, or permission to ACT.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/266 -p 'test_*.py' -v
    python3 aether/266/transport_compare.py --bundle evidence.json --out hold.json

The program never connects to any network, alters a repo, or authorizes physical action. Frozen historical phases remain unchanged.

Next AETHER-267-RS: obtain a real independently retained challenge pin via verified acquisition, correlate separately recorded TLS sessions, and reject indistinguishable self-issued evidence.
