# P3.66 — Dual-storage loss and rollback stress

Date 2026-10-09. Executed Node.js local script with 8 scenarios and 16 assertions against the existing P3.65 AnchoredWitness. Test status PASS_WITH_TWO_CONFIRMED_GAPS, **not** a security pass.

Two failures: (1) deleting both primary record and independently stored anchor file while preserving their directories, and (2) rolling both records back to the absent state, can cause a conflicting signature for the same epoch to be issued. Both directories removed fails closed because the anchoring directory must already exist. Isolated corruption or deletion of only one record did not lead to conflicting signing in these scenarios. This is a simulation of storage loss/rollback, not a demonstration of real power failure or a proof of distributed durability.

P3.65 remains unsafe against coordinated deletion or rollback of both stores. Next step is an independently trusted non-rollbackable witness watermark or durable signing service and an audit of missing/wiped signing history. Protecting multiple ordinary files on one trust domain does not ensure a monotonic watermark.
