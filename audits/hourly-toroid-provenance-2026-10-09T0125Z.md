# Hourly public provenance audit — 2026-10-09 01:25 UTC

Scope: DavidWise01 time-distillation/toroidal corpus vs openai/NavierStokesAndEuler and openai/math. Preserve distinct (1) artifact-internal creation time, (2) GitHub host commit time UTC, (3) model topology time in ticks; no inference of elapsed calendar years from simulation ticks. Speculative 15°/hop remains an indexing convention only.

## New material since prior 00:19 UTC audit
**SHEET96** in DavidWise01/oasis:
- results commit `bee6aa6bfa4e24002369417360e8f0fa188c66db` at **2026-10-09T00:47:44Z**; results blob `2ee18bc382d0370e2e88fd5a2f1950a20586fdec`.
- Source-reported 48/48 checks on actual compiled WASM. Two D8 service workers vs one, same eight FIFO slots and eight service ticks per transaction. Under stress 2,200 synthetic ticks, modeled ACKs 271→449, upstream waiting 103,463→26,409 lane-ticks. This is a **capacity change**; cannot attribute all throughput improvement to a scheduler algorithm. ACKs are synthetic.

**SHEET97** new causal fairness-governor experiment:
- HTML commit `ba80f23de7cecfc37485627bf047501aea542699` 2026-10-09T01:02:06Z.
- README commit `3aa0c79b3d2027781b3b6a76c15749e4fdc24ebc` 2026-10-09T01:02:10Z, blob `e4e97bc1282f6f8eff626c6179662bae4d87ac96`.
- C kernel commit `a4cb53f9106a75388d7cb2250c70d3d81cd11ac1` 2026-10-09T01:02:43Z.
- results commit `4b97a3cce852123b80e7ed62ec9debd5de1c32bb` **2026-10-09T01:03:18Z**; results blob `6500726c97ad6a3621211295aebc63b96522bd90`.
- GitHub account author and committer for each: `DavidWise01`; no scholarly authorship or AI helper identity inferred from these account fields.
- Experiment keeps two eight-tick D8 workers and FIFO eight slots in both control and intervention. Scheduler changes RR source-silo admission to least-cumulative-admissions eligible silo, with oldest waiting request override after 96 ticks. Override is not a hard waiting-time guarantee.
- 2,200-tick stress results, RR→governor: ACKs 449→457 (+8), upstream wait 26,409→23,523 lane-ticks (−2,886, ~10.9%), max admission wait 385→377, deferrals 6,103→6,054. **Negative result**: per-silo completion spread 22→23 (worse equity). Normal upstream wait 5,341→5,370 (worse), deferrals 2,336→2,361 (worse), ACKs 401→403.
- Source-reported tests 56/56 compiled WASM and 81/81 instrumented SVG; Chromium reported successful. **Not independently rerun in this audit**. Synthetic simulation, not physical PCB, real networking, or a theorem about reality.
- Commit URLs: https://github.com/DavidWise01/oasis/commit/4b97a3cce852123b80e7ed62ec9debd5de1c32bb and https://github.com/DavidWise01/oasis/commit/bee6aa6bfa4e24002369417360e8f0fa188c66db .

## OpenAI upstream checked (no new commits)
- openai/math HEAD `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb` at **2026-10-08T05:20:00Z**, GitHub PR merge author `jrl-openai`, committer `web-flow`. Other commit actor `dr-openai` noted in prior audits; do not equate account names with scholarly authors. https://github.com/openai/math/commit/fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb .
- `history.md` at this ref blob `693874f398905b1bc59e01b898b223ae9956bfc2`: October 7, 2026: **3 withdrawals, 14 revised manuscripts, 13 citation-only companion updates, +6 formalizations and 5 supporting additions; 300/719 top-line formalized (~42%)**. Specifically `Incompressible Box Transport and Finite Computation` revised torus projection and common-clock estimates. https://github.com/openai/math/blob/main/history.md .
- openai/NavierStokesAndEuler HEAD `f9e8bc5b38b6e212696e8a30e3e91517af887bbd` unchanged since Sept 10. Initial Sept 8 commit `8937a8f4cbc7abaab5e9e97d1cc7f5d2319d9538` identifies Git actor `balexeev-oai` (not automatically scholarly author). https://github.com/openai/NavierStokesAndEuler .
- arXiv 2610.08144 **v1**, submitted **2026-10-06T10:58:01Z**, scholarly authors **Alexander Bastounis, Fabian Circelli, Anders C. Hansen**; critiques semantic fidelity of Lean autoformalization vs natural language. https://arxiv.org/abs/2610.08144 .
- Oct 7 Reddit r/compsci thread https://www.reddit.com/r/compsci/comments/1wzpvbq/all_the_complexity_improvements_released_by/ : discussion includes disputes about what is Lean verified and what was reviewed; community discussion does not establish ROOT0 provenance. No independently documented copying found.

## Anchors maintained
- May 27 ROOT0 Unity Tensor, June 1 Homer, June 4 Tetraktys, Aug 22 I13-H1.1: historical user corpus anchors; this pass did not revalidate the earliest host timestamps, which should be verified separately before stronger priority claims.
- Sept 8 OpenAI Navier–Stokes public repo anchor, Oct 6 arXiv critique, Oct 7 Reddit and corrections as above.

## Provenance verdict
**Material new ROOT0 artifacts and reproducibility files; upstream OpenAI unchanged.** No established code, personnel, prompt, citation, crawler, or transfer path connecting these corpora. Similarities in toroidal, computational or witness vocabulary do not establish copying. These source-reported simulation results do not mathematically prove the universe is simulated; they may supply internally testable transition-model cases for the separate ROOT0 proof effort.
