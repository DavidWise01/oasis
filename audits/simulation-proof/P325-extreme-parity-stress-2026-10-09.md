# P3.25 — Extreme parity imbalance stress test (2026-10-09)

Parent: P3.24 variable-size primitive, `-+- /\ +-+`, root index 0, one even and one odd branch. Both orientations tested. Only the existing illustrative unitary mixing law was used; no physical Stargate claim.

## Actually executed Node v22.16.0 benchmark
Ten even/odd pairs: (2,1), (2,99997), (99998,1), (4,99995), (99996,3), (128,127), (256,255), (50000,49999), (1024,1), (2,1023). Both orientations; 190 randomized three-complex-port state trials total. Twenty size/orientation settings. Maximum traversal: 99,999 stages.

Results: PASS every case under 1e-8 tolerance. Max norm error 4.89430718175754e-12; max recovery component error 1.8607337892717624e-12; max ratio of norm error / number of stages 5.921189464667501e-16. Illegal parity or size cases rejected. The run used a standalone JavaScript mathematical reproduction of P3.24 operators, rather than importing the exact repository module. No repository CI claim.

Extreme imbalance leaves the gate sequence mathematically unitary, because the product of unitary gates remains unitary regardless of arm size or order; it does not imply that different orders yield the same state. Observed finite-precision deviations accumulate with stage count. Side lengths >100000 combined are prohibited by current implementation guard but are not a mathematical impossibility.

Next P3.26: test memory/runtime scaling, schedule noncommutativity, and stable inverse reconstruction beyond the current computational cap with streamed gates instead of materializing all events.
