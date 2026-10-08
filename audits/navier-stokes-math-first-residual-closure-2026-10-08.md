# Navier–Stokes math-first audit: residual closure at Sections 9–10
Date: 2026-10-08
Source: https://cdn.openai.com/pdf/32d9f210-8b73-45e0-91bc-82a30aef8a9a/navier-stokes.pdf
Status: STATEMENT-TRACED / NOT INDEPENDENTLY PROVED

## Why this check
The mathematical correctness of a construction must be assessed separately from Lean verification or semantic translation.

## Source-specific findings
- Section 9 introduction (printed page 100): The source states that nonzero angular harmonics are removed via Proposition 7.2; primary amplitudes changed by (7.31); zero auxiliary averages by (8.20); five-equation system (8.25) corrects three support defects while preserving two moment constraints. Proposition 9.6 is claimed to gain a fixed positive power of epsilon per correction cycle.
- Proposition 9.9 (printed p. 114): assembles local velocity/pressure, claims divergence-free and residual decay, with proof dependent on Lemmas 9.7, 9.8 and 5.4.
- Proposition 10.1 (printed pp. 117–118): localizes via u=curl(c A)+c B e_theta; for axisymmetric c,B, div u=0 because div curl=0 and angular derivative of c B=0. This checks divergence of the localized field (conditional on assumed regularity), NOT the nonlinear momentum equation.
- Equation (10.5) DEFINES f to equal residual R(u,p). The hard statement is its smooth extension through t=1 with compact support, not algebraic PDE equality for t<1.
- Lemma 10.2 claims uniform convergence of spatial/time force derivatives at t=1. Its proof invokes Theorem 3.1(ii), exact exterior heat flow (3.5), local residual flatness (3.4), and derivative estimate (10.9).
- Exterior azimuthal profile pressure is normalized by radial integration and obeys partial_r p = K^2/r. Mathematical validation of this formula would require verifying profile and signs carefully.

## Independent check and limits
For smooth axisymmetric c(r,z,t), B(r,z,t), div[c B e_theta]=(1/r) partial_theta(c B)=0. div curl(c A)=0. Consequently the localization identity has no missing top/bottom closure requirement in divergence alone. This identity does not establish existence/smoothness of the original A or all-order residual flatness.
No independent estimate verification or numerical counterexample here. The precise unresolved target is whether (9.18) yields hypotheses of Lemma 5.4 and whether (3.4) truly gives (10.9) uniformly through every region and seam.

## Follow-up falsification
Try to find a single failed quantifier/uniform bound across q->0, r->0 or dyadic band overlaps. Audit frequency/label uniformity claimed in Lemma 9.8 and the summation of Proposition 9.9. Then inspect all-order force-derivative continuity in Lemma 10.2.

No copying, gravity omission, or toroidal-streamline failure is inferred solely from the picture.
