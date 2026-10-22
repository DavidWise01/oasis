# Step 10 — POSIX crash-consistency and concurrent writers

Run: `python3 docs/y2038/check_step10.py`.

Commit sequence: acquire an exclusive advisory `fcntl.flock` on stable lock file; write pending record; flush/fsync file; validate staged content; atomically `os.replace` within one directory; fsync directory; release lock.

Local Python run: six checks passed. Twelve concurrent child processes each submitted a valid IT3S record; the final record was valid and one of their submitted values.

Caveats:
- This is a cooperative POSIX locking design and not portable to Windows unmodified.
- File systems, storage hardware, and abrupt power failure can have different durability semantics. No real power-cut or fault-injection simulation was run.
- The SHA-256 record digest is unkeyed, providing corruption detection rather than authentication.
- Only the final value is confirmed, not preservation of every update; no append-only transaction history.
- Stale pending files are overwritten on next successful commit. Production recovery needs formal startup and rollback policies.
- This uses assert statements in test code; run without Python optimization.
