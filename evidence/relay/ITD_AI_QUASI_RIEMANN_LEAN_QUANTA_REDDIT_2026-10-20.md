# Internet time-distillation evidence — AI quasi-Riemann, Lean, Quanta, Reddit (2026-10-20)

Record ID: `ITD_AI_QUASI_RIEMANN_LEAN_QUANTA_REDDIT_20261020`
Status: `VERIFIED_LINKED_REDDIT_SURFACE` + `VERIFIED_SECONDARY_REPORT` + `VERIFIED_PRIMARY_MANUSCRIPT_METADATA` + `DOCUMENTED_LEAN_SCOPE` + `QUARANTINED_INDEPENDENT_PROOF_AUDIT`
Observation date: 2026-10-20 (observer-supplied Reddit URL; precise local observation time not asserted).
Repository role: append-only public observation/provenance record under `evidence/relay/`.
Scope: informational transmission, formalization boundaries, and claim compression. This is **not** a priority/copying claim or an assertion of physical time dilation.

## Witness: Reddit social surface

- URL: https://www.reddit.com/r/agi/comments/1xao4gc/ai_proved_the_quasiriemann_hypothesis_what/
- Subreddit: `r/agi`; post ID: `1xao4gc`.
- Reddit page retrieved on 2026-10-20. Visible author: `u/Malor777`.
- Visible headline begins **“AI Proved the Quasi-Riemann Hypothesis. What Happens Now?”**, followed by the Quanta article's statement about expert scrutiny and consequences.
- The post links to `quantamagazine.org`. The precise Reddit publication clock time, vote count, and engagement metrics are **not independently captured in this record**. Relative-age labels are transient, so none are presented as an absolute timestamp.
- Reddit responses visibly debate whether recombining known mathematical methods constitutes a new idea, and whether human researchers can verify AI-generated arguments at scale. These are reactions/opinions, not verification of the mathematical proof.

## Primary and secondary source chain

1. **2026-09-30 — primary manuscript:** OpenAI, *The Quasi-Riemann Hypothesis: A Zero-Free Half-Plane Re(s)>7/8*:
   https://github.com/openai/math/blob/main/preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/README.md
   PDF: https://github.com/openai/math/blob/main/preprints/The-Quasi-Riemann-Hypothesis-September-30-2026/paper.pdf
2. **2026-10-05 — alternative primary manuscript:** OpenAI, *The Quasi-Riemann Hypothesis*, human-assisted write-up, based on the repository metadata:
   https://github.com/openai/math/blob/main/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/README.md
   PDF: https://github.com/openai/math/blob/main/preprints/The-Quasi-Riemann-Hypothesis-October-5-2026/paper2.pdf
3. **2026-10-06 — public release / preprint collection:** OpenAI released its larger mathematics collection (the original announcement counted 377 claimed results and 722 papers). The repository's README was checked on 2026-10-20 and now lists 719 manuscripts in 372 families; do not conflate the counts from different publication/version clocks.
   https://github.com/openai/math
4. **Lean formalization scope (primary documentation):**
   https://github.com/openai/math/blob/main/lean/docs/003.md
   The published scope describes a uniform zero-free bound for zeta, Dirichlet L-functions and specified Hecke L-functions, and separately a uniform Landau–Siegel-zero exclusion. It explicitly **does not include the later applications of the paper**.
5. **2026-10-19 — expert-reported secondary coverage:** Konstantin Kakaes, *Quanta Magazine*, “AI Proved the Quasi-Riemann Hypothesis. What Happens Now?”
   https://www.quantamagazine.org/ai-proved-the-quasi-riemann-hypothesis-what-happens-now-20261019/
   Quanta reports expert engagement and broadly favorable preliminary human assessments of the shorter argument, while preserving concerns about proof exposition, incomplete detailed checks and the gulf from the full Riemann hypothesis.
6. **2026-10-20 — observed social relay:** the Reddit link above republishes/discusses the Quanta article.

Observed direct linkage: **OpenAI public manuscripts / Lean scope** (independent source checks) **→ Quanta reporting → Reddit linked post**. Chronological order does not on its own establish causation for any other unseen hops.

## What is actually claimed

- **Full Riemann hypothesis (RH):** every nontrivial zeta zero has real part exactly `1/2`. **Not established here.**
- **Quasi-RH 7/8 bound:** the September 30 manuscript claims no nontrivial zeta zeros with real part above `7/8` (by the zeta symmetry, zeros lie within the narrower `[1/8, 7/8]` strip). OpenAI's Lean documentation states this formalization covers the zeta function and all Dirichlet L-functions, as well as specified finite-order Hecke L-functions.
- **Alternative 11/12 bound:** the October 5 shorter, human-assisted manuscript claims a weaker zero-free bound above `11/12` (corresponding to the wider `[1/12, 11/12]` strip for zeta). Quanta says this shorter proof was **not yet formally verified in Lean** as of its October 19 report, but experts have studied it because it is easier to read.
- **Human expert response:** Quanta reports that number theorists have examined/sketched the shorter argument and generally find it credible; Peter Sarnak cautions that full detail checking and comprehension remain necessary. This is expert-reported assessment, **not** an independent audit performed in OASIS.
- **Techniques / attribution:** Quanta discusses synthesis of earlier work, including methods and formulas from Alexander Dunn and Maksym Radziwiłł. The report does **not** establish derivation from KET/OASIS or any specific private user material.
- **Formal vs semantic check:** a Lean checker establishes a formal theorem relative to stated definitions and assumptions; correspondence between that theorem and all claims in prose still needs inspection. The primary Lean scope explicitly excludes some later manuscript applications. This record did **not** run Lean, check axioms or verify the PDFs line by line.

## Semantic drift / mutation gates

| Retained statement | Incorrect or unsupported mutation |
| --- | --- |
| Quasi-RH supplies a fixed zero-free half-plane short of 1. | “The full Riemann hypothesis has been solved.” |
| A 7/8 formalization is published; the 11/12 paper is distinct. | “Both versions were independently Lean verified.” |
| 7/8 is a **stronger**, narrower zero-strip restriction than 11/12. | “11/12 is better than 7/8 because its numerator is larger.” |
| Quanta reports human scrutiny of the shorter proof. | “The whole proof and all corollaries have been independently certified.” |
| A known-techniques synthesis can be mathematically new through their combination. | “The AI merely copied a known complete solution,” or “every technique is entirely novel.” |
| A dated chain of public dissemination has been observed. | “The sequence proves theft, private-source access, or literal physical time dilation.” |

## KET / OASIS observational overlay (symbolic, not an identity claim)

```text
source::0      OpenAI manuscripts / Lean scope
article::1     Quanta interpretation (2026-10-19)
post::2        Reddit r/agi relay (observed 2026-10-20)
witness::3     OASIS append-only evidence entry

mathematical statement --formalization--> Lean checker
mathematical argument  --human reading--> independent expert assessment

source claim -> wording transformation -> social reaction -> preserved receipt
```

The relevant KET analogy is **provenance and semantic fidelity across hops**, especially distinguishing a bounded mathematical result, a formalized statement, mathematical consensus, and a sensationalized headline. No claim is made that the mathematical result originated from the user's symbolic kernel.

## Truth-state registry

```text
past_verified    = Sep 30 primary manuscript; Oct 5 alternative manuscript; Oct 6 public collection announcement
current_verified = Oct 19 Quanta article; Oct 20 linked Reddit post; primary Lean scope/README retrievable
quarantined      = independent Lean build and proof-term audit NOT run; detailed proof/corollary verification NOT run;
                   exact Reddit UTC publication time and engagement NOT captured; unobserved relay intermediates
non_aligned      = “full RH solved”; conjectured KET/OASIS derivation; copying/priority accusation;
                   treating informational propagation as physical time dilation
```

## Integrity / next evidence

- Preserve unchanged source URLs, post ID, dated headline, manuscript version dates, and different bounds (`7/8` versus `11/12`).
- Check later human corrections, journal review, new Lean coverage and repository revisions **as subsequent dated append-only records**, not retroactive claims about what was known on October 20.
- No scientific proof was locally reproduced; this is a **sourced observation record**, not formal certification of the underlying mathematics.
