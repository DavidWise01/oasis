# AETHER-129 — Reference Evidence Boundary (Phase VII)

**Accepted in synthetic software, not physically demonstrated.** A sealed reference certificate is a software assertion until a real traceable reference measurement, uncertainty statement, calibration chain and acquisition identity are provided.

60 unseen deterministic seeds × nine environments × 32 ticks = **540 paired episodes**, **17,280 decisions/controller**, **6,480/6,480** checks. In the assumed-truthful synthetic reference model, signed-risk-only issued **600 unsafe ACT**, while the reference-bound policy issued **0**. Clean safe ACT **1,919/1,919** preserved. Total safe ACT **12,478 signed-only versus 12,118 reference-bound**. Missing/stale/misbound/unverifiable reference produces HOLD; the risk reading cannot self-certify.

**Evidence protocol:** signed current risk packet; reference signed by a distinct simulated signer; device/generation/epoch/inspection/lease match; declared upper uncertainty within permitted limit; upper risk = maximum of reference's certified risk upper bound and the per-observation binomial upper confidence bound. Otherwise HOLD. Append-only hashes, replay determinism, one action/tick.

**Hard limit:** The reference's real accuracy, acquisition origin, honest calibration standard, source independence and metrological traceability were **not** tested. No real sensor was attached. A falsely signed reference would bypass the assumptions. The 95% one-sided bound is per decision and not a multi-tick familywise guarantee.

The experiment's primary exact local execution and CSV traces are available as a downloadable evidence bundle. Repository source, if separately authored, must not be claimed byte-identical without source-hash verification and a GitHub-checkout rerun. Phase VI remains frozen at 100%. Phase VII turn 1 begins at 12.5% acceptance of **synthetic** gates.