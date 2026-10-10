# P3.87 — Interrupted witness publication recovery (2026-10-09)

Executed in Node v22.16.0 against P3.86 dependencies; **19/19 assertions PASS**. Recovery checks the retained external witness, validates the local signed append-only chain, and publishes only the exact next locally signed record using external compare-and-swap under the existing lock. It never creates a new signature. Tests covered successful reconciliation, idempotence, resumed signing, remote outage and retry, signed manual lock clearance, and a genuine SIGKILL orphan-lock exercise.

**Critical trust boundary:** External RetainedWatermark remains an in-memory nondurable test double. Manual lock clear requires signed operator authorization AND verified offline quiescence; the API's boolean flag itself cannot establish quiescence. No durable replay prevention for recovery authorizations; concurrent live lock clearance remains unsafe if procedural requirements are violated. Atomic durability of remote/local publication, power-loss fsync, and full distributed consensus remain unproven.

The conceptual `-+5 + 1` outer topology and OSI/100-layer projection are preserved. Source+test ZIP delivered as P3.87 conversation attachment.
