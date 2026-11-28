# AETHER-279-RS — Cross-Database Readback & High-Water Reconciliation

The read-only tool uses one SQLite connection to ATTACH the AETHER-276 receipt database and AETHER-278 high-water database, and issues a transaction containing the SELECTs. It compares signer registry SHA-256, challenge count, receipt count, three-source uniqueness per challenge, last recorded rotation head, and a preserved high-water SHA-256 chain. A separately provided anchor digest can expose historical checkpoint removal or rewriting.

**Strict limitation:** ATTACH with a read transaction is not a distributed commit protocol. Across databases maintained and committed by separate writers, reads may not prove a globally atomic moment in time. The tool *detects contradictions*, it does not establish cross-DB write atomicity, independent signer ancestry, authenticated external custody, or physical authority. The high-water and receipt databases remain unchanged.

Tests:
    python3 -m unittest discover -s aether/279 -p 'test_*.py' -v

Read-only audit:
    python3 aether/279/crossdb.py --receipt-db /tmp/aether276.sqlite --highwater-db /tmp/aether278.sqlite --anchor external-anchor.json --trusted-anchor-sha256 <64hex> --out hold.json

All results remain operational HOLD and physical qualification 0%. Earlier phases and freezes preserved.

Next AETHER-280-RS: a single-write atomic journal design or externally synchronized read barrier with independently retained receipt-counter anchors, without treating duplicate origin data as independent witnesses.
