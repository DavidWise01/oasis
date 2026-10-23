# Experiment 007 — duplicated SU(3) triplet, 8 states

Date: 2026-10-22. 8D representation **3 ⊕ 3 ⊕ 1 ⊕ 1**, with identical fundamental color triplet transformations and 2 singlets.

Hamiltonian H=(C tensor I3) ⊕ S, where C is a Hermitian 2x2 matrix with nonzero off-diagonal coupling and S is a Hermitian 2x2 singlet Hamiltonian. The eight embedded generators are diag(lambda_a/2,lambda_a/2,0_2).

Local NumPy execution:
- invariant Hamiltonian max commutator error 0
- deliberately color-selective perturbation commutator error 0.1
- 8D evolution unitarity error 2.1504908166564602e-15
- state norm error 1.1102230246251565e-16
- first-triplet to second-triplet transition amplitude 0.41402795501717166
- singlet leakage 0 by block diagonal construction
- allowed triplet-to-triplet coupling block rank 3
- 7/7 assertions passed.

Interpretation: allows transitions between two equivalent copies of the color triplet without breaking *global* SU(3). These are multiplicity/flavor transitions, not color-changing transitions or a prediction of new particles. No CERN event data were used.

Reproducible package provided in conversation as cern_exp007.zip.
