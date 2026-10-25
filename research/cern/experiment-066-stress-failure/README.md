# PRIM 066 — Stress-to-failure state −1

Classical spring-shell stress test, not quantum gravity. Mass 1 kg, spring stiffness 1 N/m, damping 0.12 N·s/m, resonance drive frequency near 0.9964 rad/s; dt=0.001 s; shell wall 0.30 m; restitution coefficient 0.60; failure triggered after accumulated wall collision dissipation >=0.020 J.

Drive forces 0.01, 0.02, 0.03 and 0.05 N survived up to 40 s. Drives 0.10, 0.15 and 0.20 N entered `-1` at 14.451, 8.401 and 8.229 s respectively. Impacts per case: 0,0,0,3,2,1,1. The energy ledger shows a finite numerical residual (~1.23e-4 J max). The failure trigger is a modeling assumption, not measured shell strength. No leader, no quorum. Full script, output CSV and JSON are available in the `prim_exp066.zip` conversation artifact.
