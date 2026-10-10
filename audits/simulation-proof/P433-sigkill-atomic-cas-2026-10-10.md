# ROOT0 P4.33 — CAS-only witness and in-transaction SIGKILL (2026-10-10)

Local Node v22.16.0 test: **28/28 assertions PASS**, repeat **211.653 ms**. Four separate child processes were terminated with real SIGKILL after acknowledged checkpoints: transaction-start, inserted intent, updated signed checkpoint but prior to commit, and after SQLite COMMIT. Reopening database showed epoch zero for three precommit points, epoch one for postcommit. Recovery verified signed retained checkpoint. Competing intent refused after winning branch; precommit competing intent could proceed. StrictCasWitness intentionally does **not inherit** P430 ExternalWitness, so the old raw `publish()` interface is absent. Node's node:sqlite remains experimental.

**Limits:** isolated local SQLite transaction atomicity, not distributed two-phase atomicity, nonrollbackable storage or power-loss durability. Privileged code with direct DB access can still modify data. No second host and no independent key custody. Regession uses checkpoint-hook invocation to coordinate deterministic kills, not exhaustive instruction-level fault injection.

Source, SIGKILL worker, test, five dependencies, JSON and README are in P4.33 ZIP, SHA256 `c1acd99c702420df316d4f5a0177b449d3d62938fde99192176b7be74cc45e8c`. This commit records the audit; executable files are packaged locally.

Next P4.34: synchronize missing dependency chain and complete GitHub clean-checkout CI, then test recovery in witness process separate from controller.