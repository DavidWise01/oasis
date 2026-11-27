# AETHER-259-RS — Multi-Process CAS & Restart Evidence

This phase launches **separate Linux/Windows-compatible Python child processes**, each with its own SQLite connection, competing against the same initial ledger head. A barrier time coordinates their attempts. It uses the AETHER-258 `BEGIN IMMEDIATE` CAS primitive and verifies committed event hashes, receipt hashes, and final head after all processes exit.

A fixed child begins a SQLite write transaction, changes the head, and exits with `os._exit(17)` **without committing**. A new connection then reads back the local ledger and checks that SQLite rollback preserved the head. This child is a benign test process; it is not an external operator or production writer. No signaling, killing, lock release, or physical ACT occurs.

Run:

    python3 -m unittest discover -s aether/259 -p 'test_*.py' -v
    python3 aether/259/process_recovery.py --db /tmp/aether259-test.sqlite3 --workers 8 --out /tmp/aether259.json

Use a fresh scratch database; the command writes local files. Test results demonstrate only local OS/SQLite behavior, not independent external custody, actual multi-host atomicity, power-loss durability, or authenticated witness signatures. An interrupted child is not a power-loss test. The harness is deliberately fail-closed with operational authority HOLD and physical qualification 0%. No earlier freezes changed.

Next AETHER-260-RS: produce bounded immutable receipt exports and verify them after restart with separate hash snapshots and external provenance qualification.
