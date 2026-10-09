# P3.73 — signed checkpoint rollback test (2026-10-09)
Tested with local Node.js v22.16.0: 11/11 assertions PASS. Ed25519 signed checkpoint binds context, epoch, count and SHA-256 head. An old internally valid SQLite snapshot created via VACUUM INTO was restored. It was rejected when compared with separately retained latest signed checkpoint. Tampering, wrong key, missing trusted checkpoint, and older checkpoint replay were rejected.

**Critical limitation:** verification of the same old snapshot succeeds when the external 'trusted' reference is rolled back to its matching old, correctly signed checkpoint. A signature authenticates origin, not freshness. The trust file here is an ordinary local JSON file, not an independently durable or nonrollbackable authority. SQLite WAL copy while open can have platform-specific issues; test used a SQLite-generated consistent snapshot. This is not a production anti-rollback service.

The outer symbolic containment `-+5 + 1` stays intact; the +1 anchor must ultimately provide a non-rollbackable trusted watermark.
