# AETHER-291-RS — Paired Remote Object Readback and Claimed Retention

AETHER-291 provides a bounded, opt-in HTTPS readback of the **same exact object bytes** from three approved endpoints in **two separately invoked, locally ordered acquisition windows**. Every window checks the source URLs, out-of-band pinned trust-record digest, Ed25519 signatures on previously supplied AETHER-290 retention metadata, and original AETHER-264 transport observation integrity. All original raw response bytes and claimed retention records are preserved in a canonical SHA-256-linked SQLite journal together with three unique observation nonces for that window. A second window requires the same artifact bytes, pinned trust root and URLs.

The forensic reader reconstructs both window hashes and retained remote response bodies, checks nonce conservation, detects changed responses or history, and optionally compares historical window sequence/hash to a supplied prefix pin. It never treats two adjacent local invocations as proof of elapsed time; caller-supplied signed retention metadata is NOT observation of remote object-store locking or WORM controls. Even distinct HTTPS hosts and declared independent controller graphs can share a single source ancestry. A live independently witnessed cross-time trial is **not** performed automatically.

The tests use offline mocked HTTPS and ephemeral Ed25519 keys; no real endpoints are contacted. Previous AETHER phases and freezes remain unchanged.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/291 -p 'test_*.py' -v

Each window is a separately invoked opt-in operation, using distinct nonce strings:
    python3 aether/291/two_window_readback.py capture --db /tmp/aether291.sqlite --artifact export.json --trust trust.json --pin <sha256> --urls approved-urls.json --retention-records signed-retention-records.json --nonce first-window-nonce-291
    python3 aether/291/two_window_readback.py capture --db /tmp/aether291.sqlite --artifact export.json --trust trust.json --pin <sha256> --urls approved-urls.json --retention-records signed-retention-records.json --nonce second-window-nonce-291
    python3 aether/291/two_window_readback.py audit --db /tmp/aether291.sqlite --prefix-seq 1 --prefix-sha256 <sha256>

The retention metadata records are used to check signed provenance claims but no independently authenticated physical/object-store immutability is established. Operational authority HOLD, physical qualification 0%.

Next AETHER-292-RS: independently attested provider object-version metadata, externally established observation intervals, and multi-origin ancestry qualification without promoting user-supplied controller graphs to custody authority.
