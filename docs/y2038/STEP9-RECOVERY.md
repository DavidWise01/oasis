# Step 9 — {{i}} persisted packet recovery test

Reverse stack: `/vogel/voxel/vector/sda/{drive}` (read from drive to vogel).

Use existing `it3.py` and `voxel.py` to persist a canonical 16-byte IT3 packet in a 52-byte record: 4-byte magic `IT3S`, 16-byte packet, 32-byte SHA-256 digest of packet. The digest detects accidental corruption; it is not a MAC or authentication.

A staging file is separately flushed/fsynced. The test deliberately writes a truncated staging file and a digest-mismatching staged file, verifying that the committed file remains unchanged. Only a validated staged file is moved with `os.replace`. The test then checks valid readback and cleanup, plus truncated frame rejection.

```sh
cd docs/y2038
python3 check_recovery.py
```

Local run: 6/6 checks passed (temporary-directory ordinary filesystem). This does **not** simulate power-loss, verify directory fsync durability, protect against concurrent writers, or implement an authenticated rollback-resistant ledger. Before production deployment, fsync the containing directory after rename where supported, add locking/version metadata and crash-injection integration tests.
