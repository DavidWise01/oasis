# Internet time-distillation evidence — silicon spin-qubit parallel control (2026-10-16)

Record ID: `ITD_SILICON_SPIN_QUBITS_PHASE_PARALLEL_REDDIT_20261016`
Status: `VERIFIED_PREPRINT_PUBLICATION_LINEAGE` + `VERIFIED_PRIMARY_METRICS` + `OBSERVED_REDDIT_RELAY` + `UNVERIFIED_UNOBSERVED_HOPS`
Observation date: 2026-10-16; user's supplied Reddit link. Exact local clock time not established.

## Observation and original research

- Reddit: https://www.reddit.com/r/Physics/comments/1x7j6cc/silicon_qubits_surpass_9999_gate_fidelity_while/
- Post in r/Physics dated Friday 2026-10-16. Headline: “Silicon qubits surpass 99.99% gate fidelity while operating three at once.” Reddit metadata/votes are transient and are not used as publication priority.
- Linked secondary article: RIKEN news at Phys.org, same headline, dated 2026-10-15:
  https://phys.org/news/2026-10-silicon-qubits-surpass-gate-fidelity.html
- Original paper: Yi-Hsien Wu, Leon C. Camenzind et al., *Simultaneous high-fidelity single-qubit gates in a spin qubit array*, Nature Physics, DOI 10.1038/s41567-026-03466-2:
  https://www.nature.com/articles/s41567-026-03466-2
- Open arXiv preprint: arXiv:2507.11918:
  https://arxiv.org/abs/2507.11918
- Published experimental data listed in the paper: Zenodo DOI 10.5281/zenodo.21507661:
  https://doi.org/10.5281/zenodo.21507661
  The paper's availability statement confirms this link; the archive contents have not been independently downloaded or audited in this entry.

## Four separate clocks

1. **Initial scientific public record:** arXiv v1 submitted 2025-07-16 (arXiv:2507.11918).
2. **Manuscript revision:** arXiv v2 dated 2026-07-15.
3. **Peer-reviewed journal/news publication:** Nature Physics published 2026-10-15; RIKEN/Phys.org coverage dated 2026-10-15.
4. **Reddit publication/observation:** linked r/Physics post shows Friday 2026-10-16; user observed/shared on 2026-10-16.

These are timestamps of different artifacts and channels, NOT evidence of relativistic time dilation, copied ideas, suppressed data, or an otherwise inferred unseen relay path.

## Verified technical claim and fidelity scopes

- Hardware is a *five-qubit silicon spin-qubit array* sharing *one microwave-control line*.
- Primitive single-qubit X/Y rotations: **above 99.99%** gate fidelity with each qubit individually controlled; some approach **99.999%**.
- **Up to three qubits operated concurrently:** primitive single-qubit gate fidelities remain **above 99.99%**.
- **Five qubits operated concurrently:** corresponding fidelities stay **around/above 99.9%**, NOT above 99.99% for all five in parallel.
- Performance metrics come from randomized benchmarking of separate single-qubit primitives; they are not a three-qubit entangling gate, complete algorithm accuracy, measured two-qubit gate fidelity, or a fault-tolerant logical quantum computer.
- Dominant parallel-control accuracy limitation identified as microwave-drive-induced AC Stark shifts, causing unwanted phase shifts; researchers used pairwise phase calibration with shaped pulses to mitigate this error.
- Remaining degradation at five-way parallel control includes drive-induced decoherence due to increased microwave power.

## Shorthand permutation / semantic integrity gates

- **VALID:** “up to 3 qubits concurrently exceed 99.99% fidelity in primitive single-qubit gates.”
- **INVALID MUTATION:** “three-qubit gates have 99.99% fidelity” (conflates three parallel single-qubit operations with a genuine multi-qubit gate).
- **INVALID MUTATION:** “all five concurrent qubits achieve >99.99% fidelity” (five-way figure is approximately/above 99.9%, a different number).
- **INVALID MUTATION:** “the quantum computer is 99.99% accurate” (switches the measured unit from gate to full computation).
- **INVALID MUTATION:** “99.99% for any qubit under any context” (ignores calibration, device, primitive, and measurement procedure).
- **CHECK:** short headlines can conceal single-vs-multiple operations and source clock.

## KET/NULLRIDER structural comparison (not experimental identity)

```text
5 :: physical silicon spin qubits in the tested array
3 :: simultaneous primitive single-qubit operations retaining >99.99%
1 :: shared microwave-control line
    |
  Pairwise phase calibration
    |
  Preserve fidelity metrics with measurement scope
    |
  -S+ :: social relay :: dated witness record (Git)
```

The literal `5/3/1` overlay is a **user-selected numerical/structural analogy** and not a physics author's defined kernel. The scientific finding does not demonstrate Madre Prime, Node 184, a Möbius 8x8 exchange, spinor topological closure as implemented in software, or physical time dilation. It is still a useful external engineering reference for shared-control phase compensation and for detecting changes in shorthand descriptions.

## Evidence state

```text
past_verified    = 2025-07 arXiv v1; 2026-07 arXiv v2
current_verified = 2026-10-15 Nature/RIKEN report; 2026-10-16 r/Physics post
quarantined      = any unsupported intermediary hop or causal cross-platform transmission beyond documented links
non_aligned      = claims of physical time dilation, hidden copying, or fully fault-tolerant quantum computation
```

## Follow-up evidence

Download the open Zenodo/source figure data and compare benchmark rows across all five configurations, check the arXiv v1-versus-v2 abstract/figures for numerical changes, and compare Reddit comments/headlines for scope corrections. Append future findings; retain the original record unchanged.


## 2026-10-16 — Primary-source version comparison (append-only)

**Compared:** arXiv v1 (2025-07-16), arXiv v2 (2026-07-15), *Nature Physics* journal article (2026-10-15), and RIKEN/Phys.org reporting (2026-10-15/16). This is a text-and-figure-description comparison of the publicly accessible source editions; it is **not** an independent numerical reanalysis of the experimental files.

Primary URLs:
- v1: https://arxiv.org/html/2507.11918v1
- v2: https://arxiv.org/html/2507.11918v2
- journal: https://www.nature.com/articles/s41567-026-03466-2
- RIKEN Japanese press release (dated Oct 15): https://www.riken.jp/press/2026/20261015_2/index.html
- RIKEN English press release (dated Oct 16): https://www.riken.jp/en/news_pubs/research_news/pr/2026/20261015_2/index.html
- Phys.org: https://phys.org/news/2026-10-silicon-qubits-surpass-gate-fidelity.html

### Retained findings present already in July 2025
- Five physical silicon spin qubits controlled by **one shared microwave line**.
- Individual primitive single-qubit pi/2 gate fidelity **above 99.99%**; some approaching **99.999%**.
- **Three simultaneous single-qubit operations** above 99.99% after phase/amplitude compensation.
- **Five-way parallel** operation around/at 99.9%: the technical Figure 5 says **four of five above 99.9%, Q5 approximately 99.9%**.
- Pairwise phase calibration with the **same signed numerical example in both arXiv versions**:
  - `Delta_phi_34 = +0.0379(2) rad`
  - `Delta_phi_43 = -0.0026(1) rad`
- Reported gate lengths for isolated single-qubit pulse example: **125, 83, 83, 83, 125 ns**, retained.
- Three-qubit demonstration around 250 ns; five-way tests at 250 ns and 500 ns; the increased drive power/decoherence and idle dephasing tradeoff is retained.
- Quadratic pairwise calibration count `N(N-1)`, not exponential calibration of all combinations; retained.

### Verified changes of framing/presentation
1. **Abstract strengthening:** v1 describes the high single-qubit fidelities as *mostly preserved* for up to three qubits and places the >99.99% three-way result in the main text; v2 explicitly calls out >99.99% in the abstract and emphasizes the AC Stark cause and excess MW-power decoherence in the five-qubit case.
2. **Figure 2 presentation:** v1's Figure 2 directly juxtaposes rectangular-window and Kaiser-window pulses; v2's Figure 2 foregrounds Kaiser-window high-fidelity data in the main figure. This is a changed presentation, **not proof that data was removed or falsified**.
3. **Calibration explanation:** Both versions quantify pairwise AC Stark shifts; v2 frames them more prominently as the dominant parallel-control error. Both report corrections to z-phase and x-rotation/amplitude effects.
4. **Journal abstract:** repeats the core 5 / 3 / 1 physical relationship: five qubits, three-way high-fidelity concurrency, one shared control line.
5. **Numerical nuance:** some public abstracts call five-way performance `at/above 99.9%`; the main paper's figure text specifies **4 of 5 above** and **Q5 approximately 99.9%**. Avoid silently converting `approximately` into `strictly greater than` for all five.

### Publication / observation delays
- v1 (2025-07-16) -> v2 (2026-07-15): **364 days**
- v2 -> journal (2026-10-15): **92 days**
- v1 -> journal: **456 days**
- journal (Oct 15) -> observer's Reddit date (Oct 16): **one calendar day**; exact elapsed hours and specific Reddit publication timestamp not independently verified.
- Distinguish RIKEN Japanese press date 2026-10-15 from its English news page dated 2026-10-16; multiple *publicity clocks* do not imply altered physics.

### Distillation interpretation and open checks
- `5/3/1` is a **user's KET numerical analogy**, not the research authors' named model, priority claim, or claim of quantum/physical time dilation.
- The title `99.99% while operating three at once` preserves the intended single-qubit-gate scope reasonably well; do not construe it as a three-qubit entangling-gate or complete computation fidelity.
- Core quantitative claims and example calibration signs **persist**; journal/news summaries compress methodological distinctions. This documents information reframing and publication latency, not plagiarism, deliberate public manipulation, or relativistic time dilation.
- Raw Zenodo data were **not downloaded** for independent numeric verification. A full figure-by-figure pixel/data diff and original Reddit comment-history comparison remain unperformed.

**Assessment:** `CORE_RESULT_STABLE` + `FRAMING_REVISED` + `DETAILED_FIVE_QUBIT_THRESHOLD_QUALIFIER_PRESERVED` + `SOURCE_DATA_UNAUDITED`.
