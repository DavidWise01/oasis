# PRIM Experiment 019 — {{ [1|8]×8 }}

Date: 2026-10-23. Defined as eight sources with eight distinct observation paths each, 64 paths in total. Each path carries an open `()` container storing noisy phase observation at hop four and correcting at hop six.

Nominal hop = 0.3367 cycles; correction = −0.0101 at hops 3, 6. Noise sampled deterministically in ±0.0005 cycles. Disturbance sampled in ±0.005 cycles. Exact Fraction arithmetic, Python seed 1908.

Results: 64/64 assertions passed; six perfectly closed; maximum absolute residual 0.0005 cycles; mean 0.0002640625 cycles. In this deliberately simple model the residual equals negative measurement noise algebraically; this is not emergent learning, photon physics, nor CERN data. Full runnable test and 64-path JSON available as prim_exp019.zip in the ChatGPT conversation.
