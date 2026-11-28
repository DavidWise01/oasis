# AETHER-299-RS — Actual SigV4 Signer Parity & Crash-Safe Handoff Qualification

AETHER-299 directly calls the **existing AETHER-297 owner_bound_ledger.sign()** implementation and compares its canonical request SHA-256 and HMAC signature against AWS botocore SigV4Auth for identical GET / HEAD metadata requests. This avoids qualifying an independently rewritten look-alike signer instead of the actual production logic. Tests use fixed synthetic test credentials only; do not put real AWS credentials in fixture files.

The create-only external handoff packet is generated after read-only verification of the AETHER-297 SQLite evidence journal and a historical prefix supplied out-of-band. It captures the exact journal head and historical prefix, declared recipient, and declared ancestry-pin digest, but not the underlying credential-bearing requests, object path or source metadata. O_EXCL prevents overwrite, fsync flushes the packet and parent directory, and immediate readback checks exact persisted bytes. Failpoint tests exercise before-file-fsync, after-file-fsync and before-readback interruptions; a partial file is preserved rather than deleted and retry does not clobber it.

**Critical limits:** a local packet is not a signed receipt from an external custodian; independently witnessed custody and independent immutable high-water retention are NOT established. A declared recipient and ancestry pin are not proof of actual controller independence. The local source journal and locally retained pin may be rolled back together. SigV4 client signing parity does not authenticate the S3 service, a bucket's independent owner or the contents' custody. No live AWS sandbox is contacted. All outputs explicitly remain operational HOLD, physical qualification 0%.

Offline regression:
    python3 -m pip install 'botocore>=1.35,<2'
    python3 -m unittest discover -s aether/299 -p 'test_*.py' -v

CLI:
    python3 aether/299/handoff_qualification.py parity --fixture SYNTHETIC-ONLY-case.json
    python3 aether/299/handoff_qualification.py handoff --db /tmp/aether297.sqlite --out /tmp/aether299-handoff.json --seq 1 --head <sha256> --recipient independently-operated-custodian --ancestry-pin <sha256>
    python3 aether/299/handoff_qualification.py audit --packet /tmp/aether299-handoff.json --db /tmp/aether297.sqlite --pin <sha256>

The handoff operation never uploads data or pretends to receive external acceptance. The caller must arrange independent off-platform storage and collect separately verified acknowledgment evidence. All earlier phase files and freezes are unchanged.

Next natural bound AETHER-300-RS: acquire actual signed external custody acceptance under independently verified custodian keys; validate remote head and receipt ancestry and repeat after a separately verified observation interval, while maintaining physical ACT HOLD.
