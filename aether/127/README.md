# AETHER-127 — Failed unseen-drift stress (preserved)

**FAIL — no progress awarded. Phase VI remains 6/8 = 75%.**

The AETHER-126 scheduler was imported **without policy edits** and exposed to eight unseen sensor conditions, 60 new seeds each, 32 ticks per episode. Across **480 paired episodes** and **15,360 decisions per policy**, all **5,760 replay, hash-chain, causal action and resource-budget checks passed**.

The non-negotiable zero-unsafe gate **FAILED**: fixed calibration **696** unsafe authorizations; adaptive calibration **662**. Both failures were isolated to (a) nonlinear monitor blindspot: fixed **421**, adaptive **403**, and (b) nonlinear midrange distortion: fixed **275**, adaptive **259**.

The response function was specifically designed to *pass all four calibration probe inputs* 32/96/160/224 while under-reporting ordinary risk values in the 35–90 or 35–80 count bands. Consequently, **full calibration also fails**; increasing the frequency of the same finite calibration probes cannot eliminate this failure.

Adaptive purchased **47,640 probes** versus fixed **61,440** (13,800 / 22.5% saved), and synthetic cost **727,587.2 versus 769,086.4**. Neither economy matters while the safety gate fails. Clean scenario safe ACT adaptive 1,917 vs fixed 1,919.

**Reproducibility note:** The original test imported the local archived `/mnt/data/aether126/experiment.py` with SHA-256 `9fde4f39ca3806869556561bb6f1a8654ed108f74ae53e9914ccb3631d9d4426`. The repository reproduction script imports its `../126/experiment.py`; byte identity between these two copies has **not yet been verified**. Hence matching the published CSV from a fresh GitHub checkout must be independently rechecked; the local numerical CSV is authentic to the local execution, not claimed as remote CI proof.

**Next bound: AETHER-127B — hidden, randomly located interior micro-probes with guarded coverage**, or record the domain as unobservable and HOLD. No choice/quorum/Byzantine machinery; single deterministic controller. This cannot guarantee against all selective nonlinear deception; prove explicit coverage or fail closed.
