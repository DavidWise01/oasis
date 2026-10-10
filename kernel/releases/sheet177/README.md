# SHEET 177 — Signed WAL and Crash Recovery Gate

Local tests: S177 20/20 PASS; S176 20/20, S175 26/26, S174 20/20, S173 22/22 PASS; 108/108 aggregate focused checks.

Implemented independently keyed Ed25519-signed WAL-head checkpoints, hash-chain and monotonic count validation, unanchored-tail quarantine, torn-record rejection and true child SIGKILL after injected post-prepare exception. The exception unwinds cleanup before SIGKILL; therefore no assertion of a hard crash during fsync or an abandoned lock. Physical host and WAL anchor still share a failure domain. No remote database atomicity or cross-host consensus.

Executable release ZIP: SHEET177-signed-WAL-crash-gate.zip 40,308 bytes, SHA-256 c7e6a81e512543882a2d6f781f5016473bf3f5a8d9ccff822e350779fe308d92. Full code and preserved predecessor source in ZIP.

Next SHEET 178: hard-kill before lock cleanup, independently managed durable witness storage, and target-cursor reconciliation after uncertain commit.
