# Experiment 004 — maximum-depth stress checkpoint

Date: 2026-10-22.
Model: 8-slot Boxy (3 active color states plus 5 inert auxiliaries); SU(3) Tori transforms the active subspace; repeated sequential operations are factorized. This is NOT an 8^N-dimensional entangled-state simulation.

## Python / NumPy numerical result
All depths 1, 2, 3, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 100000 passed tolerance 1e-9.
At 100000:
- Maximum unitarity error 5.595494099399233e-15
- Maximum cumulative state-norm error 9.658940314238862e-14
- Auxiliary leakage exactly zero (by block-diagonal construction)
- Adjoint SU(3) generator-span closure error 3.037639350626798e-16
- Runtime approximately 4.06 seconds in local runtime for 100000.

## Interpretation
This validates numerical stability of sequential SU(3) evolution encoded in a larger 8D Hilbert space. It does not validate an 8-color physical theory, quark compositeness, a literal toroidal geometry, or any particular physical sub-femtometre hierarchy. A single 8-slot box carries a 3D invariant color subspace and inert complement; block-diagonal evolution trivially forbids leakage.

## Next falsification test
Introduce nonzero coupling between active and auxiliary sectors, then quantify leakage, deviation from SU(3) and observability against high-energy data.

Code: experiment-004-depth/depth_test.py
