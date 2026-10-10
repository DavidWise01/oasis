# P3.91 — Blockade reconciliation stress test

Local Node.js 22 test: **24 of 24 assertions passed**. The `{-{+{%}+}-` guard was extended with a reconciliation path that compares the local fencing lease and the retained witness epoch, then publishes an existing lease by external compare-and-swap without minting an additional token. Faults: interrupted publication (quarantine), outage (fail closed), restored witness (reconciliation), idempotent retry, subsequent takeover, stale-owner writes, deterministic interleaved acquisitions, rollback of a coherent local database snapshot, and deletion/reset of the independent witness.

The test **reproduced vulnerability** on resetting the volatile witness: old state can be issued again. Additional open security issue: local-ahead-by-one does not prove *authorized acquisition intent*; a malicious or tampered local store may have advanced the epoch. The trusted witness remains an in-memory mock; no independent durable anti-rollback guarantee or atomic distributed commit. The racing-acquisition test is deterministic interleaving, not process-load or kill-testing.

Executable sources, dependencies, tests and JSON measurements are provided in the P3.91 ZIP. Next P3.92: separately authenticated durable intent and witness CAS acceptance, plus real multi-process race and kill injection.
