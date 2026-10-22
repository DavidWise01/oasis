# Step 13 — Raft election and log-matching model

Run: `python3 docs/y2038/step13_raft.py`.

Model-only three-node election and log matching. It demonstrates vote restrictions based on the latest term/index, term monotonicity, rejection of stale terms, matching previous-entry terms, catch-up, and majority gating. Eight local checks pass.

**Not a complete or durable Raft implementation.** Terms/votes/logs are in memory, reachability is supplied by the caller, there are no RPCs, real timers, persistent quorum certificates, commit index, leader completeness enforcement, read safety, snapshots, or complete Raft conflict resolution. An old leader cannot be rejected on a remote node until that node observes a higher term. Do not use this prototype for real consensus or deploy it as a distributed store.

**Next:** Step 14 replaces the simplified model with a tested Raft library or a full protocol implementation with persisted stable state, append/commit rules, and network fault simulation. Production readiness remains targeted at Step 20, subject to verification.
