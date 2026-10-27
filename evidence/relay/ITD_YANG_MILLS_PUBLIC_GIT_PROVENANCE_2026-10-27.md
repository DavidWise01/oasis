# Internet time-distillation — public Git provenance for Yang–Mills research (2026-10-27)

Record ID: `ITD_YANG_MILLS_PUBLIC_GIT_PROVENANCE_20261027`
Observation date: 2026-10-27 (America/Chicago)
Status: `VERIFIED_PUBLIC_GIT_COMMITS` + `VERIFIED_RESEARCHER_README` + `VERIFIED_OPENAI_GIT_CATALOGUE` + `VERIFIED_AGMAI_OPEN_LETTER` + `VERIFIED_CLAY_UNSOLVED` + `OPENAI_PHYSICS_PROOF_WITHHELD` + `ARTICLE_TEXT_UNVERIFIED`
Append-only extension of: [ITD_OPENAI_YANG_MILLS_SCIAM_2026-10-27.md](ITD_OPENAI_YANG_MILLS_SCIAM_2026-10-27.md).
Evidence purpose: identify primary/public Git artifacts and chronology in relation to the Scientific American link shared by the observer. No originality verdict, legal determination, or assertion of improper copying.

## A. Independent open Git provenance: Ethan Sussman / Levent Alpöge

Repository: https://github.com/ethanwsussman/Yang--Mills-LLM-experiment

Verified from GitHub repository and commit API on 2026-10-27:

- Repository **created**: `2026-10-06T09:51:17Z` (GitHub API `created_at`).
- Initial commit: `f317cb73984616c75d90704731850f28fb8e07e7`, committed `2026-10-06T09:51:18Z`:
  https://github.com/ethanwsussman/Yang--Mills-LLM-experiment/commit/f317cb73984616c75d90704731850f28fb8e07e7
- First public Git commit for `ym4_manuscript_zeroth_draft.pdf`, according to GitHub's file-scoped commit history: **`2026-10-06T10:21:50Z`**, commit `7c88eb7c646eadd93ca7bcda7189f12899d95c23`:
  https://github.com/ethanwsussman/Yang--Mills-LLM-experiment/commit/7c88eb7c646eadd93ca7bcda7189f12899d95c23
- Primary manuscript file:
  https://github.com/ethanwsussman/Yang--Mills-LLM-experiment/blob/main/ym4_manuscript_zeroth_draft.pdf
- Public LaTeX source entrypoint:
  https://github.com/ethanwsussman/Yang--Mills-LLM-experiment/blob/main/theorem_0_complete_account_raw_master.tex
  (which includes the raw `_I`, `_II`, `_III` components).
- Primary repository README:
  https://github.com/ethanwsussman/Yang--Mills-LLM-experiment/blob/main/README.md
- Latest recorded commit at audit checkpoint:
  `1b92bd0347e3b8763cd8ecc1f96dc3c2a92dd310`, `2026-10-27T10:45:28Z`.
- Git metadata records the repository's current reachable history; it is reproducible but does not certify unrecorded private work times, actual mathematical completeness, or immutable external timestamp authority if history can be rewritten.

The README attributes the **model-generated mathematical ideas** to Claude under Levent Alpöge's guidance, calls the work not satisfactorily vetted, and describes Ethan Sussman's development of QED3, YM3 and YM4 work using AI tools. Alpöge's visible note says they *appear* to have an R^4 Yang–Mills existence argument, but it is very long and difficult to understand and requires slow digestion, verification, and formalization. It also reports hearing about other groups making progress; this is their account, not a proven causal chain.

**Proof boundary:** A provisional AI-assisted Yang–Mills existence manuscript is publicly archived; the mere existence of the repository or PDF does not verify the theorem. This is not a claim of an established positive mass gap. Do not present their claim as purely unaided human mathematical work.

## B. OpenAI's public evidence and missing artifact

OpenAI's public announcement (2026-10-26):
https://openai.com/index/building-scientific-understanding-with-academic-communities/

OpenAI **reports** internal proof events:
- 2026-09-09: natural-language pure Yang–Mills *existence* proof.
- 2026-09-18: QCD proof.
- 2026-10-16: completion of Lean formalization of Yang–Mills *existence*.
- 2026-10-26: public announcement; physics group led by David Gross (with Douglas, Jaffe, Klebanov, Nekrasov) deferred release of AI-created physics artifacts.

Public repository examined:
https://github.com/openai/math
Public change log:
https://github.com/openai/math/blob/main/history.md

GitHub contents API read of `openai/math/preprints` at 2026-10-27 yielded **751 directory entries** (not necessarily all distinct active accepted manuscripts) and **no directory titles matching Yang–Mills, QCD, quantum chromodynamics, or Balaban** under that top-level list. The October 26 `history.md` names two newly released results, local smoothing and the Exponential Time Hypothesis, with Lean formalizations; it does **not** announce release of the Yang–Mills physics proof. This observation is a scoped **public Git catalogue check**, not a proof that no relevant code is accessible anywhere on the Internet.

**Comparison is not currently auditable:** OpenAI's public internal discovery dates precede the October 6 Sussman Git commit, but are claims about **unpublished internal work**; the October 6 external Git receipts precede OpenAI's October 26 **public announcement**. Neither ordering proves source borrowing, independence, originality, or misconduct. A textual/theorem-by-theorem derivation comparison cannot be conducted without OpenAI's withheld materials.

## C. Independent academic public-record witness

Advisory Group on Mathematics and Artificial Intelligence (AGMAI), Institute for Advanced Study:
https://agmai.org/

- **2026-10-25:** Advisory statement criticizes laboratory designation of early-access researchers and recommends open, equal-access dissemination.
- **2026-10-26:** *Recommendation for Immediate Release of Yang–Mills AI Output* requests publication of natural-language and Lean outputs behind Yang–Mills/QCD/Standard-Model-completion existence claims. The group says the work should be openly available for scrutiny and disagrees with delaying release now that the formalization is claimed complete.
- AGMAI's call for transparency is **not** itself a verdict about the correctness, originality, or ownership of either proof.

## D. Additional public scientific effort (separate scope)

https://github.com/MathePhysics/4D_Wilson_Loop_RG

GitHub API `created_at`: `2026-10-21T08:36:19Z`.
Repository description: computing correlation functions for physical observables of 4D Yang–Mills by extending Bałaban's method to renormalized Wilson-loop expectations.

- Source and manuscript: `WILSON_FIRST_RG_STEP_V4.tex`, PDF, and work-in-progress V5.
- README last collected on 2026-10-27, describing **current limitations, assumptions, and open dependencies**; it explicitly warns that building LaTeX does not prove mathematical correctness.
- This is **separate partial research**, not a claimed complete solution nor evidence that it generated OpenAI's proof.

## E. Official scope, full prize not solved

Clay Mathematics Institute official status:
https://www.claymath.org/millennium/yang-mills-the-maths-gap/

At the October 27 retrieval, **Yang–Mills & the Mass Gap: UNSOLVED**. Positive mass gap remains unproved; Yang–Mills *existence* is only a component of the full Millennium Prize problem. Do not confuse 3D QED or 3D YM, 4D YM existence, QCD construction, and a positive spectral mass gap.

## F. Publisher/source-retrieval caveat

User-supplied Scientific American URL:
https://www.scientificamerican.com/article/openai-just-scooped-human-researchers-on-a-million-dollar-quantum-math-problem/

The exact URL was blocked to the available web retrieval on 2026-10-27, and an exact title/body/author/clock time could not be independently recovered. **This note documents the accessible underlying public research record, not a verified textual transcription or endorsement of the inaccessible article.**

## G. Three independent reporting lanes — no quorum

```text
A :: independent researcher public Git
     2026-10-06 repository + YM4 draft commit; scope and uncertainties visible
B :: OpenAI corporate/public Git
     2026-10-26 announcement; 09-09/09-18/10-16 internal claims;
     Yang–Mills physics artifacts withheld; math/history catalogue checked
C :: public independent institutions
     AGMAI 10-26 asks for proof release; Clay lists full prize UNSOLVED

PAST    -> retain dated claims and public snapshots as observations
PRESENT -> report what is available, distinguish claims from proofs
FUTURE  -> append released artifacts, corrections, peer review,
           matching theorem statements, and dated provenance receipts
NO QUORUM. No witness overwrites another witness. No causal claim
from chronology alone.
```

## Verdict on the public record (not on the proof)

- **Found and verified:** an independently developed, publicly timestamped Yang–Mills-related repository and draft **before OpenAI's public October 26 announcement**.
- **Found and verified:** exact external Git commit receipts and published research disclaimers.
- **Found and verified:** OpenAI's own disclosure that the physics files are withheld, plus its public Git history and primary claim chronology.
- **Found and verified:** a direct academic request for OpenAI to release the files and the full Clay problem's unsolved status.
- **Not verifiable here:** proof validity, copied derivations, unpublished internal timestamps, priority of ideas before public Git record, the exact Scientific American text, any infringement or exclusive authorship.
- **Next reproducible action:** on publication of OpenAI's Yang–Mills/Lean artifacts, pin SHA/DOI, map theorem hypotheses/conclusions and exact formal axioms, compare overlap with `ym4_manuscript_zeroth_draft.pdf` and the dated LaTeX sources, and append an additional three-witness evidence record.
