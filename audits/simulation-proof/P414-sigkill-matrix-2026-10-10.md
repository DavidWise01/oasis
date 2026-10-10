# ROOT0 P4.14 — controlled SIGKILL crash matrix (2026-10-10)

**Result: 25/25 assertions PASS**, six independent Node v22.16.0 child processes terminated with actual SIGKILL following acknowledged crash checkpoints. Passing runs: 248.785 ms and 254.364 ms, including child startup. No actual hardware power removal.

| Killed after | Recovered state | Decision |
|---|---|---|
| Before file creation | UNINITIALIZED | first authorized initialization permitted |
| File created, before JSON write | QUARANTINE / malformed-reservation | second genesis blocked |
| JSON write, before fsync | QUARANTINE / reserved-without-authority | second genesis blocked |
| File fsync | QUARANTINE / reserved-without-authority | second genesis blocked |
| Directory fsync | QUARANTINE / reserved-without-authority | second genesis blocked |
| Authority SQLite commit | ACTIVE | second genesis blocked |

**Found and repaired a genuine recovery bug:** original P4.13 code treated malformed JSON and missing file identically as UNINITIALIZED. P4.14 changes it to return UNINITIALIZED *only* on ENOENT; unreadable or malformed existing reservations are quarantined. Regression and crash worker committed alongside patch to P4.13 recovery module.

Caveats: process-kill tests cannot prove power-failure durability; an IPC checkpoint is not an arbitrary instruction boundary. SQLite local authority and shared-filesystem registry have no external irreversible witness; coherent rollback or deletion of all history remains a live threat. Symbolic model ({- {+ {%} +} -} without spaces = `{-{+{%}+}-}`), 200 layer clock, and OSI concepts are not physically measured here.

Next P4.15: independently persisted monotonic deployment witness; signed recovery intent and post-crash replay/rollback probes.