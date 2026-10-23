# PRIM Experiment 018 — open inference pocket `()`

Date 2026-10-23. Six-hop exact-rational test with phase increment 0.3367 cycles/hop, correction −0.0101 at hops 3 and 6, and injected +0.005 cycles at hop 4.

New operation: an open `()` inference container observes `actual_phase - nominal_phase` at hop 4 and carries the captured value across hop 5 to correction at hop 6.

Results: no inference carrier ends at 2.005 cycles (+0.005 drift); accurate carrier ends at 2.000 cycles (zero drift). Three exact-rational assertions pass: residual without carrier, inference capture at hop 4, correction at hop 6. Full runnable Python and exact-fraction results in ChatGPT `prim_exp018.zip`.

**Boundaries:** Perfect sensing and memory are assumed; there is no independent noise, stale inference, learning, or physical photon inference. The result validates memory-assisted correction, not spontaneous emergent behavior.
