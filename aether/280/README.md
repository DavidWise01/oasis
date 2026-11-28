# AETHER-280-RS — One-Journal Receipt and High-Water Commit

This new isolated local SQLite implementation closes the AETHER-279 cross-database write gap. An atomic BEGIN IMMEDIATE transaction verifies three signatures against a sealed registry, inserts one challenge and exactly three source-distinct receipts, calculates committed counts, and appends the SHA-256-linked high-water checkpoint **before one database commit**. Any signature, replay, stale head, or conservation failure rolls back everything.

The design uses one SQLite file, WAL, synchronous=FULL, UNIQUE constraints and foreign keys. Signed receipt statements bind challenge, source, session, session nonce, payload digest and current sealed registry digest. A checkpoint has a parent hash and exact committed counts; readback validates hashes and count conservation. This is a fresh single-journal design and does not migrate or modify AETHER-276 and 278 databases.

There are still important limits: claims about key custody and controller independence are self-supplied; no external source or independent witness is authenticated; the entire SQLite file and out-of-band pin could be rolled back together. No operational ACT is permitted.

Test:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/280 -p 'test_*.py' -v

CLI:
    python3 aether/280/atomic_journal.py bootstrap --db /tmp/aether280.db --keys signer-records.json --registry-pin <64hex>
    python3 aether/280/atomic_journal.py commit --db /tmp/aether280.db --bundle signed.json --registry-pin <64hex> --expected-head <64zeros-or-current-head>
    python3 aether/280/atomic_journal.py inspect --db /tmp/aether280.db

All CLI paths remain authority HOLD and physical qualification 0%. Earlier freezes are preserved.

Next natural bound AETHER-281-RS: crash-consistency qualification and externally pinned journal-head recovery; independently retained checkpoint custody still remains unverified.
