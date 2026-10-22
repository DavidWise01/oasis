# Step 15 — partition and competing-leader safety (bounded simulation)

Run `python3 docs/y2038/step15_partition.py`.

Scenario: initial leader A commits, network partitions A | B,C, isolated A cannot commit, connected B,C elect B and commit, partition heals and lagging A catches up. The original committed prefix is unchanged.

Local result: 8/8 deterministic assertions passed.

## Scope and restrictions
This is a constrained model, **not a complete Raft implementation**. It uses a global coordinator for elections, immediate in-memory acknowledgments, no messaging delay, packet loss, disk failure, randomized partition histories, independent clocks, persisted votes, commit-term restrictions, or real multi-host services. Payloads are labels, not validated IT3 envelopes. Committed prefixes must never be overwritten in production, and real leader fencing requires fully specified protocol messaging and persistence.

The test demonstrates this single scenario, not a proof that split brain is impossible under every schedule.

Remaining: Step 16 authenticated peer messaging; Step 17 snapshot/restore; Step 18 fault injection; Step 19 formal + multi-host checks; Step 20 operational hardening.
