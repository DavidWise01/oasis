# AETHER Phase VII — Physical Measurement Assurance

**AETHER-134 bounded reference-drift synthetic gate passed. Phase VII: 6/8 = 75%. Physical validation: NOT performed.**

| Turn | Bound | Status | Phase completion |
|---|---|---|---:|
| 1 | 129 Physical reference evidence boundary | **ACCEPTED (synthetic)** | **12.5%** |
| 2 | 130 Reference instrument provenance and traceability | **ACCEPTED via 130B (synthetic)** | **25%** |
| 3 | 131 Bounded reference uncertainty certificate | **ACCEPTED — synthetic** | **37.5%** |
| 4 | 132 Device response regularity test | **ACCEPTED — synthetic** | **50%** |
| 5 | 133 Probe insertion and same-path verification | **ACCEPTED via 133B (synthetic)** | **62.5%** |
| 6 | 134 Reference drift and recalibration economics | **ACCEPTED — synthetic** | **75%** |
| 7 | 135 Unseen independent instrument stress | Planned | 75% |
| 8 | 136 Integrated empirical-gate freeze | Planned | 75% |

## AETHER-134 — Bounded reference drift and adaptive calibration economics

- Local **400 paired synthetic episodes**, 50 new seeds × eight conditions × 32 ticks = **12,800 decisions per policy**; **5,600/5,600** replay, chain, one-way action, ordered counter, fail-closed, zero-unsafe and budget checks passed.
- Fixed policy purchases **11,900 calibrations**, adaptive policy purchases **3,650**, saving **8,250 / 69.3%** under the calibrated model. Both had **zero unsafe ACT, 9,000 safe ACT and 1,000 safe HOLD**; no clean availability regression.
- Adaptive scheduling uses five ticks for low certified drift and two for high drift; a changed instrument generation requires fresh calibration. A risk upper bound adds the last calibrated bias, a certified maximum inter-calibration drift allowance, and certified sensor noise.
- Synthetic scenarios: clean, slow drift, high drift, abrupt shift, noise burst, expired reference, route substitution and new instrument.
- **Essential physical limitation:** This experiment assumes a trustworthy reference reveals actual calibration bias, drift certificates are valid over time, and a separately protected same-tick alarm detects abrupt jumps. **Undetected abrupt physical drift, a forged reference, or false ingress evidence can invalidate zero-unsafe conclusions.** No physical instrument was tested; software checks are not physical validation.
- Local tested Python SHA-256 `c633be2486fffb814f98e24975b78b40631e108dfc3915a854488b603f739710`. GitHub source is independently authored and exact numerical replay from checkout has **not** been confirmed.
- [AETHER-134 reproducible source, local numerical summary and interactive HTML](134/) committed. Live GitHub Pages deployment unverified.
- **Turn 6 accepted on constrained synthetic gates: Phase VII 6/8 = 75%. Next AETHER-135: unseen independent instrument stress.**

## AETHER-133B — Signed calibration does not prove shared acquisition path

- **AETHER-133 original test FAILED:** 240 of 5,600 signature-integrity checks failed due to a test-fixture bug: packet mutations retained the previous `mac` field before computing a new HMAC. This invalidated several attack cases and understated signed-only unsafe ACT as 2,000. The failure, source and evidence are frozen at [133/](133/); **no phase credit**.
- **AETHER-133B corrected test PASS:** the signer now excludes the existing `mac` before creating a fresh signed mutation. 40 new seeds × 10 acquisition-path conditions × 24 ticks = **400 paired synthetic episodes**, **9,600 decisions per policy**, **5,600/5,600** deterministic checks.
- The comparator accepts ordinary signed sensor packet/calibration but does not establish same physical acquisition. It made **3,200 unsafe ACT**. The ingress-bound controller required matching **device, epoch, tick, counter, path, probe path, risk path, protected port, nonce, challenge digest and calibration validity**, and made **zero unsafe ACT**.
- Clean and legitimate instrument rekey both preserved **960/960 safe ACT**; overall both controllers retained **6,400 safe ACT** in the test model. Missing or mismatched ingress receipts force HOLD.
- The failed and corrected **executed local Python source snapshots**, 5,600-check CSVs, seed results and decision traces are copied into GitHub, with original failures retained.
- **Physical limitation:** The protected ingress signing root and reported physical route are *assumed trustworthy simulation inputs*. An HMAC signature **cannot physically prove path identity or reference-standard accuracy**; no physical injector/device verification was performed. A forged protected ingress or selectively probe-aware sensor remains outside the guarantees.
- [Accepted AETHER-133B source, results, checks, traces and interactive Pages HTML](133b/) committed. Live GitHub Pages deployment unverified.
- **Turn 5 accepted under synthetic software gates: Phase VII 5/8 = 62.5%. Next AETHER-134 — reference drift and recalibration economics.**

## AETHER-132 — Device response regularity between certified calibration points

- **400 paired synthetic episodes**, 50 new seeds × eight sensor-response scenarios × 24 ticks = **9,600 decisions per policy**, **5,600/5,600** deterministic replay, chain, source binding, time and fail-closed checks passed in the local execution.
- Simple endpoint calibration mistakenly authorized **2,000 unsafe ACT**: **500 each** from nonlinear notch, response discontinuity, gain shift and device dropout. A 51-point interior response-regularity gate authorized **0 unsafe ACT** in these constructed fault scenarios.
- Test domain: measured risk 0–5% in **0.1 percentage-point** steps. Require current signed device/certificate identity and epoch, residual <=0.08 percentage points, and local response slope in [0.8,1.2].
- Valid clean and valid calibration rotation both preserved **1,200/1,200 safe ACT**. Overall safe ACT dropped **7,600 → 6,800**, with **800 additional safe HOLDs** caused by expired calibration certificates.
- Probe demand rose **19,200 → 489,600** (**25.5×**). These are safety/coverage tests, not resource-efficiency improvements.
- **Physical limitation:** Software directly simulates sensor response at injected probe positions. No physical device or reference standard was connected; actual instrument response, insertion secrecy, and between-probe regularity are **not verified**. Finite-point validation does not certify arbitrary nonlinear distortions or physical metrological traceability.
- Local tested Python source SHA-256 `2d850e7e5367d57bd0957a24909e3534b20facf4adf47f2dca5ed63508cab9f5`. GitHub reproducer was authored separately; byte-identical checkout replay is **unverified**.
- [AETHER-132 executable, numerical result, manifest and interactive HTML laboratory](132/) committed. Live Pages deployment remains unverified.
- **Turn 4 accepted within synthetic assumptions. Phase VII 4/8=50%; next AETHER-133: probe insertion and same-path verification.**

## AETHER-131 — Covariance-aware reference uncertainty

- **400 paired synthetic episodes**, eight reference-uncertainty ancestry regimes × 50 seeds × 24 ticks = **9,600 decisions per controller**. **5,600/5,600** deterministic integrity, replay, fresh-reference, fail-closed, and zero-unsafe checks passed in the local execution.
- Signed-only comparator assumes two ±0.004 calibration components are independent. At observed risk ≈0.018 the naive one-sigma upper estimate ≈0.02366 permits ACT under threshold 0.025, while perfectly correlated common-root components produce 0.026 and require HOLD.
- Under the synthetic modeled risk fault, naive independence authorized **2,500 unsafe ACT**; covariance-aware controller **0 unsafe ACT**. Clean safe ACT **1,200/1,200**, legitimate certificate rotation **1,200/1,200** preserved.
- Across all scenarios safe ACT **7,100 naive → 6,400 covariance-aware** and **700 additional safe HOLD**, including a deliberately missing covariance certificate.
- **Critical limitation:** Physical root ancestry, rho, and uncertainty magnitude are synthetic declared facts, not physically established. One-standard-deviation covariance arithmetic is not a validated high-confidence risk bound, and cannot itself establish metrological traceability. This is a software logic experiment, **not physical reference validation**.
- Local implementation SHA-256 `49fb21d19707e7dd6b02499563c8bbd184926fc1ffb3fe1ba6bcb448266ea654`; the GitHub-authored source is a separate implementation and its byte-identical replay against local data is **unverified**.
- [Executable and interactive laboratory](131/) committed. Live GitHub Pages deployment unverified.
- **Turn 3 accepted on synthetic criteria, Phase VII = 3/8 = 37.5%; next AETHER-132: device response regularity.**

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
