# AETHER-275-RS — Pinned HTTPS Key-Ring and Live Source Receipt Capture

This phase introduces an **opt-in live collection path** rather than relying only on caller-supplied records. It uses the previously published AETHER-264 allowlisted HTTPS collector for a separately specified keyring URL and three distinct allowlisted source endpoints. A raw keyring is accepted only when its actual body SHA-256 matches an out-of-band digest passed at the command line. Each source response must be a signed JSON record binding a fresh challenge to a payload digest and the source's key in the keyring.

The test suite mocks all HTTP connections but uses genuine Ed25519 keys and signatures, so it exercises signature checks and collection routing with no live network traffic. The CLI may make up to four real HTTPS requests only when the operator supplies the URLs, allowlist and pin. It saves raw response bytes and metadata to the output JSON. A keyring SHA-256 supplied by the same controller that produces the body is **not** independent authentication. Controller identities and custodian independence are unproven.

Run offline tests:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/275 -p 'test_*.py' -v

Opt-in external collection:
    python3 aether/275/live_capture.py --keyring-url https://registry.example.org/keyring --keyring-sha256 <trusted64hex> --challenge <freshchallenge> --allow-host registry.example.org --allow-host source0.example.org --allow-host source1.example.org --allow-host source2.example.org --out receipt.json

Replace example endpoints with authorized real public endpoints and known pinned records. The CLI deliberately returns exit code 1 and authority HOLD. No credentials or private keys are embedded. No claim of three independent custodians, external anti-rollback, or physical qualification is made.

Next AETHER-276-RS: persistent signed transport receipts, cross-run nonce replay fencing, and externally verifiable key-ring pin rotation.
