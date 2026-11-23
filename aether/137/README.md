# AETHER-137 — Physical Validation Readiness

**Phase VIII Turn 1 — synthetic software PASS, physical validation NOT PERFORMED.**

The first Phase VIII gate separates two kinds of evidence:

- A **synthetic fixture** can demonstrate deterministic packet binding, calibration traceability fields, instrument identity, acquisition continuity, uncertainty limits, and explicit `HOLD` behavior.
- **Physical action authorization** requires a real externally validated instrument and reference standard, with trusted validation of acquisition identity, calibration traceability, uncertainty and same-path behavior. None was provided, so **every operational action remains HOLD**.

## Results

Eight simulated scenarios × 50 seeds × 24 ticks = **400 episodes and 9,600 decisions per policy**. The three policies were naive signature-only, synthetic readiness/dry-run, and physical authorization. **8,400 / 8,400** replay, SHA-256 chain, temporal, single-action and fail-closed checks passed.

Signed-only had **3,500 unsafe ACT** in the engineered faults; the synthetic readiness policy had **0 unsafe ACT**, preserving **1,200 / 1,200 clean safe ACT**. The operational physical gate had **0 ACT of any kind** because no empirical reference evidence was supplied. Its clean HOLDs are intentional and do not constitute an availability success on real hardware.

The simulated defects were expired calibration, missing reference traceability, wrong device, broken same-path binding, uncertainty over limit, replayed counter, and a forged self-attested hardware-receipt claim. The fixture HMAC is not a physical trust root. Future hardware integration requires a separately validated receipt and independent uncertainty chain; the current software explicitly cannot manufacture one.

**Acceptance tracking:** 1/8 Phase VIII *synthetic readiness gates* = **12.5%**; measured physical validation remains **0%**. Phase VII remains frozen at its declared software acceptance 100%.

Source of numerical results: locally executed `experiment.py` with SHA-256 `291e3e0aa1b29cf45d78828106a105b7434fa402876a0b2a9fa65404bad32a3d`. Reproduction from a GitHub checkout should be independently checked. No physical instrument was connected.