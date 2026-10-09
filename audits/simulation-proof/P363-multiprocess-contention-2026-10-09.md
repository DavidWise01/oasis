# P3.63 — Multiprocess witness contention and termination races

2026-10-09. Tested actual 24 independent Node child processes per scenario, 72 launches total, against one shared filesystem reservation: normal concurrency, attempted asynchronous SIGKILL in an independent timer, and restart after quarantined reservation. All 13 assertions passed. The kill-race scenario terminated 7 workers. No conflicting checkpoint was accepted in any case; quarantined epoch remains unavailable (fail closed).

This is a test of process-level contention on the current local filesystem, not an assertion that SIGKILL occurred within a particular write syscall. It is not a power-loss test, a general claim of filesystem durability, or a distributed-consensus proof. The child process receives a temporary test-only private key in an isolated directory, deleted after each run. Externally authenticated checkpoint persistence is still required.
