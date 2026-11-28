# AETHER-281-RS — Crash-Recovery Forensics & Pinned Full-Journal Snapshots

Read-only inspection of the AETHER-280 atomic journal reconstructs the signer registry, full challenges, signed receipt rows, and high-water chain in **one SQLite read transaction**. It hashes the entire sorted snapshot rather than only the high-water counts. A caller supplies an out-of-band SHA-256 of a previously exported snapshot for comparisons after restart.

The regression cases include actual subprocess termination with os._exit() before/after SQLite commit, successful recovery from completed atomic writes, detected receipt removal, changing signed receipt bytes without changing row counts, registry seal alteration, high-water changes and full-journal hash mismatch. A precommit interruption must leave no committed challenge; a postcommit process exit must retain the completed transaction. These are simulated process exits, not a power-cut or filesystem crash laboratory.

A single pinned last-head digest can prove neither every historical prefix against later extensions nor independent custody of the checkpoint. A signature cannot be reverified from AETHER-280 persisted rows without the original full signed challenge statement. Both gaps are explicit HOLD boundaries. No earlier phase is modified.

Run:
    python3 -m pip install 'cryptography>=43,<47'
    python3 -m unittest discover -s aether/281 -p 'test_*.py' -v
    python3 aether/281/recovery_probe.py --db /tmp/aether280.sqlite --anchor archived-snapshot.json --trusted-anchor-sha256 <64hex> --out hold.json

Next AETHER-282-RS: signed original challenge-statement retention, checkpoint prefix witnesses, and externally retained crash-recovery evidence.
