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
