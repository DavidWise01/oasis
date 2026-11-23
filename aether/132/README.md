# AETHER-132 — Device Response Regularity

**PASS on bounded synthetic test.** Eight modeled conditions × 50 seeds × 24 decision ticks = **400 paired episodes**, **9,600 decisions per policy**, **5,600/5,600 deterministic integrity and fail-closed checks**.

A signed reference device can pass simple endpoint calibration and yet systematically underreport risk inside the domain. Four constructed defects — narrow nonlinear notch, step discontinuity, gain shift and dropout — yielded **500 unsafe ACT each** for the endpoint-only comparator (**2,000 total**). The regularity gate made **zero unsafe ACT** in these modeled scenarios.

**New gate:** 51 known-value test inputs from 0 to 5% response domain, 0.1-percentage-point apart. Require current signed instrument/certificate binding, matching acquisition epoch, residual no greater than 0.08 percentage points, and neighboring slopes between 0.8 and 1.2. A defective or expired certificate forces HOLD. Valid certificate rotation remains eligible.

**Availability / cost:** clean 1,200/1,200 safe ACT preserved, valid rotation 1,200/1,200 preserved. Overall safe ACT **7,600 → 6,800**, with **800 additional safe HOLD** from the deliberately expired certificate. Probe cost **19,200 endpoint → 489,600 full regularity** (25.5×).

**Important limits:** The synthetic model supplies known challenge response truth from the same programmed sensor function. Physical same-path insertion, protected reference provenance, concealment from a malicious device, response continuity and a bound on behavior between finite probes are not demonstrated. A real instrument can violate these assumptions. This is software logic testing, not physical metrology.

**Provenance:** local tested Python source SHA-256 `2d850e7e5367d57bd0957a24909e3534b20facf4adf47f2dca5ed63508cab9f5`. The published GitHub source is a separately authored corresponding implementation; byte-identical checkout replay **has not yet been verified**.

[Reproducer](experiment.py) · [Results](results.csv) · [Manifest](manifest.json) · [Interactive lab](index.html).
