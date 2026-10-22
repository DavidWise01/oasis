# Step 19 — bounded safety checking, not full protocol verification

Run `python3 docs/y2038/step19_verify.py`. Locally executed: **24 deterministic scenarios, 132 transition invariant checks; passed**.

The checker enumerates all distinct (initial leader, isolated node, successor candidate) permutations and 1–4 initial committed records. After each commit, partition, majority decision and healing, it checks that committed indexes are valid and every pair of replicas agrees on the shorter committed prefix. It additionally checks minority isolation and post-heal convergence.

## Explicit gap — multi-host testing not completed
The model has a shared coordinator and instantaneous simulated elections, not network RPC, real concurrency or independent storage. It is not a proof of a full Raft algorithm, cannot establish liveness under arbitrary schedules, and does not address power failures. Real multi-host verification must be done with an independently vetted consensus implementation, fault-injected network, restartable per-node WAL, signed release attestations and saved evidence.

**Step 19 status:** bounded scenario subtest PASS; multi-host and full formal verification **BLOCKED / not executed**.

**Step 20 target:** create an auditable release gate. It must remain FAIL until the outstanding consensus, persistence, auth and multi-host checks have real evidence; do not declare production readiness because 20/20 milestones have files.
