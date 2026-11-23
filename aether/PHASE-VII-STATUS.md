# AETHER Phase VII — Physical Measurement Assurance

**AETHER-130B corrected synthetic software gate passed. Phase VII: 2/8 = 25%. Physical validation: NOT performed.**

| Turn | Bound | Status | Phase completion |
|---|---|---|---:|
| 1 | 129 Physical reference evidence boundary | **ACCEPTED (synthetic)** | **12.5%** |
| 2 | 130 Reference instrument provenance and traceability | **ACCEPTED via 130B (synthetic)** | **25%** |
| 3 | 131 Bounded reference uncertainty certificate | Planned | 25% |
| 4 | 132 Device response regularity test | Planned | 25% |
| 5 | 133 Probe insertion and same-path verification | Planned | 25% |
| 6 | 134 Reference drift and recalibration economics | Planned | 25% |
| 7 | 135 Unseen independent instrument stress | Planned | 25% |
| 8 | 136 Integrated empirical-gate freeze | Planned | 25% |

## AETHER-130B — Traceability and uncertainty ancestry

- **AETHER-130 FAILED its availability gate**: certificate rotation mistakenly signed the prior signature field as part of the new payload; valid rotation safe ACT **719→319**, despite zero modeled unsafe ACT. [Failure preserved](130/); no completion credit for the failed revision.
- **AETHER-130B accepted:** 40 independent seeded trials × 10 synthetic calibration-lineage scenarios × 28 ticks = **400 paired episodes** and **11,200 decisions/policy**.
- All **5,600/5,600** deterministic replay, hash chain, source binding, fail-closed, no-unsafe and current-tick checks passed.
- Synthetic signed-only comparator authorized **3,200 unsafe ACT**, lineage/uncertainty gate authorized **0**. Across all tested scenarios both policies retained **7,597 safe ACT**, including **1,120/1,120** clean and **719/719** valid calibration-rotation ACT.
- The gate traces `ROOT-B → LAB → instrument certificate → reference serial → S1 risk observation`, matches device and generation, applies per-certificate lease, and adds bounded declared uncertainty components before risk authorization. Missing, cyclic, wrong-device, expired, tampered or incomplete ancestry forces HOLD.
- **Crucial limitation:** signed `independent_from` is only a synthetic declaration. It does not prove ROOT-B is physically independent or accurate. No physical reference was connected. Fully forged but internally coherent certificate chains may pass. Uncertainty sums ignore some correlations.
- [Corrected executable, evidence summary and interactive GitHub Pages source](130b/) committed; live Pages not yet independently verified. Generated local traces and check CSV downloadable separately.
- **Turn 2 accepted: Phase VII 2/8=25% on synthetic software gates.** Next AETHER-131: covariance-aware reference uncertainty and external provenance limits.

## AETHER-129 — The reference-to-reality boundary

- **540 paired synthetic episodes**, 60 untouched seeds × nine evidence scenarios × 32 ticks = 17,280 inspection decisions per controller; **6,480/6,480** locally executed deterministic checks.
- Signed-risk-only controller: **600 unsafe ACT** in risk-underreport case; reference-evidence-gated controller: **0** unsafe ACT in synthetic truth model.
- Clean safe ACT **1,919/1,919** preserved. Across all cases signed-only safe ACT **12,478** and reference-gated **12,118**; reduced availability occurs when valid reference evidence is absent.
- Refusal conditions include missing reference, stale inspection, wrong device, expired lease, invalid reference MAC, absent uncertainty certificate. No reference or risk packet may authorize itself.
- **No physical instrument attached.** A second HMAC signer inside software is **not physical or provenance independence**. Trust in reference accuracy, source traceability, signing keys and certificate uncertainty is assumed.
- The [AETHER-129 interactive laboratory, local results and separately authored Python reproducer](129/) are committed. Local executed source SHA-256: `c9cb8997db56401d32ee90c3e353686883de426d599f0955e65d055bb920066a`. The GitHub source has different bytes and has **not been independently rerun**. Live Pages deployment unverified.
- **Progress credited only for a synthetic contract gate.** The physical proof portion remains 0 and must not be inferred from this phase percentage.

## Invariant

One deterministic controller · fail closed when reference origin is unverifiable · no quorum / Byzantine solution · preserve all failures · no physical assurance without physical measurements.

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
