# Seed resolution: Reddit r/compsci → OpenAI math result 376 (2026-10-08)

## Identified primary sources
1. https://github.com/openai/math/blob/main/preprints/Incompressible-Box-Transport-and-Finite-Computation-September-27-2026/manuscript.pdf
2. https://github.com/openai/math/blob/main/preprints/Incompressible-Box-Transport-and-Finite-Computation-September-27-2026/build/introduction.tex
3. https://github.com/openai/math/blob/main/lean/docs/376.md
4. https://github.com/openai/math/blob/main/history.md
5. https://github.com/openai/math/blob/main/overview.tex

## Actual manuscript scope
OpenAI is the credited author in repository README; dated September 27, 2026. The associated umbrella entry is no. 376, Universal computation in forced Navier–Stokes flows. Smooth incompressible vector fields route volume-preserving affine maps on entire rational solid boxes with source/target disjointness separately, storing/evacuating boxes as needed. A fixed particle visits an observation region iff a finite machine halts. It supplies a force f=U_t+(U·∇)U−νΔU for a constructed divergence-free U (usually pressure zero). This is an expressly *forced* Navier–Stokes construction; not an unforced Navier–Stokes global regularity proof or a direct solution to the Millennium problem.
The Lean docs claim formalized subsets of sheet programs and box transports, but expressly exclude some fixed-particle and reciprocal mechanisms from certain selected formalizations. Do not equate the total claims with Lean proved statements without checking the individual theorem.

## Corrected statements evidence
openai/math/history.md says Oct 7, 2026 revision of torus-projection and common-clock estimates. The currently available README does not by itself give previous edition commit SHA or equation-level difference. Retrieve dated Git blobs/build tex versions and make direct diffs before asserting what failed.

## Comparison candidates (not evidence of derivation)
- 2026-06-01 DavidWise01/homer: 3×3×3 toroidal agent and Wiki/arXiv data routes. An information workflow, NOT mathematical volume-preserving fluid routing.
- 2026-06-04 DavidWise01/tetraktys: five quaternion-ring cells and explicit rollover test. A discrete toy oscillator, NOT an exact incompressible 3D flow.
- 2026-08-22 DavidWise01/I13-H1.1: frozen toroidal witness; read-only observation, 55,296 enumeration. Discrete symbolic witness, NOT necessarily particle observability.
- OpenAI preprint: solid boxes, deterministic timing/schedules, observation of halting and conservation of volume.
The legitimate next experiment is to compare normalized semantics: finite-state transition and witness / periodic clock / exact no-occupation outside interval vs vector field / divergence-free / determinant-one physical transport and observation. No author-change hop or copying inferred from overlap.

## Attribution
OpenAI is manuscript's collective author label. Do not use number of Git commit authors as number of researchers or AI model instances.

## Next precise tests
1. Locate prior edition and October 7 revision of build files for the same manuscript and diff torus-projection estimates and common-clock lemmas.
2. Compare the selected formalized theorem statements from BalancedBoxRouting.lean, BalancedThreeStack.lean and ForcedNavierStokesComputation.lean to the corrected text; test semantic faithfulness and assumptions.
3. Only claim causal provenance with intermediate chain evidence, not paper naming, dates or structural resemblance alone.
