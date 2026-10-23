# Experiment 005 — Boxy/Tori coupling

On 2026-10-22 an 8D Hermitian toy Hamiltonian was tested: a 3D SU(3) color sector coupled to five auxiliary states through a complex 3x5 matrix K. Coupling values: 0, 1e-5, 1e-4, 1e-3, 1e-2, 0.1, 0.5, 1. Evolution time: 10 model units, RNG seed: 5005, exact diagonalization in NumPy.

At g=0: leakage 0. At g=0.01: leakage 0.245702%. At g=0.1: 20.6637%. At g=1: 40.6735%. Full-system norm errors <= 1.6e-15. At all tested nonzero g, [H,P] != 0 for P=diag(1,1,1,0,0,0,0,0).

**Interpretation:** The 3D subspace is no longer dynamically isolated. These are synthetic mathematical results, not observed new gluons/quark substructure or CERN collision data. Next: test whether nonzero mixing can be compatible with exact SU(3) gauge symmetry without assigning the auxiliary states a nontrivial representation.

Runnable test script and JSON results are included in the ChatGPT conversation archive `cern_exp005.zip`.