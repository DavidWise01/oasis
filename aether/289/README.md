# AETHER-289-RS — Exact Remote Export Readback and ACK High-Water Audit

This phase adds explicit opt-in HTTPS readback of an AETHER-287 export from a caller-authorized endpoint. The local export is first verified against the original AETHER-286 journal, and the recovered AETHER-288 acknowledgment ledger must pass its internal hash and nonce checks before the request. The remote response is obtained via the bounded AETHER-264 TLS hostname / vetted DNS / pinned public IP collector. The exact remote response bytes must equal the canonical local export bytes; neither a semantic JSON match nor matching selected fields is accepted.

The AETHER-289 journal commits the complete original acquisition observation, requested URL, raw response base64, remote export SHA-256, acknowledgment batch sequence and head digest, and acknowledgment nonce count inside one SQLite transaction. Historical readback revalidates local hashes, stored raw bytes, nonce uniqueness and historical ACK head ancestry. A caller may also provide a separately preserved canonical high-water anchor and an out-of-band SHA-256 pin, detecting a shortened ACK ledger or replaced historical head.

**Important boundaries:** An endpoint serving matching bytes is not proof that it retained those bytes independently or immutably. A self-issued anchor digest is not a trusted external timestamp or immutable high-water service. Three custodian acknowledgments are not three independent witnesses merely because endpoints or keys differ. A local database and its supplied anchor may be rolled back together. All outputs remain HOLD and physical qualification 0%.

Run offline tests:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/289 -p 'test_*.py' -v

Opt-in readback:
    python3 aether/289/remote_readback.py capture --db /tmp/aether289.sqlite --source-journal /tmp/aether286.sqlite --ack-db /tmp/aether288.sqlite --export /tmp/export.json --url https://authorized.example.org/export.json --nonce fresh-readback-nonce-289

Forensic audit:
    python3 aether/289/remote_readback.py audit --db /tmp/aether289.sqlite --ack-db /tmp/aether288.sqlite --anchor pinned-highwater.json --anchor-pin <sha256>

Tests use mocked HTTPS transports and real temporary SQLite journal fixtures; no live endpoint is contacted by tests. Previous phases and immutable freezes remain unchanged.

Next AETHER-290-RS: externally anchored high-water acquisition with authenticated immutable retention metadata and source-ancestry evidence, never promoting signature agreement to physical authority.
