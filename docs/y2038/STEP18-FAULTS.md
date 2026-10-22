# Step 18 — deterministic fault injection

Run `python3 docs/y2038/step18_faults.py` on Linux/POSIX, with the Step 12 and Step 17 modules in the same directory.

Eight locally checked failure cases: snapshot corruption, truncated snapshot, interrupted staging, failed rename, failed directory fsync, torn WAL tail, modified WAL payload, and post-compaction chain continuity.

**Important finding:** a directory `fsync` error after an atomic rename leaves the operation's durability **unknown**; a file visible after the error is not proof it will survive a power cut. Avoid acknowledging this write as durable.

Tests monkeypatch `os.replace` or `os.fsync` in a single isolated process and use temporary directories. They do **not** emulate a power cut, storage reorder, multi-host network partitions, real consensus crash recovery, or any guarantee about storage hardware. The WAL currently detects torn tails rather than recovering them automatically.

Remaining gates:
19. formal safety verification and multi-host fault test, including real consensus implementation.
20. production release gates, operational telemetry, restore drills, independently verified durability.

Production ready: **NO**.
