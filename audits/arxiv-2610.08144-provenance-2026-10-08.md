# Provenance audit: arXiv 2610.08144 — 2026-10-08

Status: SOURCED / CONCEPTUAL OVERLAP ONLY / NO DERIVATION ESTABLISHED

Source: https://arxiv.org/abs/2610.08144
Authors: Alexander Bastounis, Fabian Circelli, Anders C. Hansen.
Version: v1, 6 October 2026, 10:58:01 UTC; 25 pages.

## Findings
1. Lean compilation alone does not establish faithful translation of a natural-language mathematical argument. Authors expressly do not declare original natural-language Navier–Stokes proof incorrect.
2. Section 3.1 compares source paper Eq. (8.19), m+4 derivative requirement, with Lean m+5 requirement. Cited upstream reference: openai/NavierStokesAndEuler commit f9e8bc5, NavierStokes/SmoothFamilyTorusInverse.lean, norm_derivativeWord_inverse_le.
3. Section 3.2 compares source paper Eq. (10.19) with a pressure-flux Lean result that includes an extra A_R term and follows a different proof. Upstream: same commit, NavierStokes/R3/PressureFlux.lean, exists_uniform_actual_pressure_flux_bound.
4. Appendix A argues arbitrarily high SCI difficulty for a precisely defined class of semantic ambiguity resolution; not a blanket impossibility for every practical Lean formalization.

## OaSIs Git audit
Repository: https://github.com/DavidWise01/oasis
README documents append-only witness/return architecture, invariants, semantic repair, and separation of deterministic output from truth.
Concepts broadly overlap with the paper's warning about representational fidelity, but code copying, author access, copyright infringement, historical priority or derivation are NOT established.

## Proposed independent verification protocol
Source statement -> translated Lean theorem -> assumptions, quantifiers, type/domain and strength of bound comparison -> independent semantic signoff -> compile test -> immutable SHA/commit provenance -> append-only witness.
Statuses: FORMAL_PASS, SEMANTIC_MATCH, SEMANTIC_MISMATCH, UNREVIEWED, QUARANTINED.

## Scope limits
This record reviews the paper and the OaSIs README and selected recent commit metadata. It is not an exhaustive commit-by-commit history of either project, nor an independent re-run of the Lean proof. Upstream discrepancy claims remain to be independently reproduced.