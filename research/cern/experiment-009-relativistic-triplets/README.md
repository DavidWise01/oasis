# Experiment 009 — Relativistic vector-like triplet toy model

Date 2026-10-22. Tested locally in Python/NumPy: nine mass-mixing configurations.

Representation: two vector-like Dirac color triplets plus two spectator singlet state slots; identical gauge representations are assumed for directly mixed fields. Color block H=M tensor I3, M=[[173,delta],[delta,m2]] GeV. m2=1200,1800,2400; delta=0,100,300. All nine numerical tests have exact zero SU(3) commutator residual and positive mass eigenvalues. Vector-like SU(3) gauge cubic anomalies cancel by representation (triplet plus conjugate triplet in left-Weyl basis).

Selected eigenmasses: for (m2,delta)=(1200,100), (163.3535,1209.6465) GeV; for (1200,300), (91.7881,1281.2119) GeV.

Lorentz compatibility follows from scalar Dirac mass operator; Lorentz transformations were NOT tested numerically. The 173 GeV lower input is arbitrary and does NOT mean a Standard Model top quark. No cross section, decay pattern, full electroweak anomaly analysis or experimentally viable region was calculated. CERN vector-like quark constraints are model-dependent: https://cds.cern.ch/record/2958774/files/ATL-PHYS-PROC-2026-020.pdf

Full runnable Python and JSON delivered in ChatGPT archive cern_exp009.zip.
