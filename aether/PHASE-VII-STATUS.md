# AETHER Phase VII — Physical Measurement Assurance

**AETHER-129 accepted on its bounded SYNTHETIC software gate. Phase VII: 1/8 = 12.5%. Physical validation: NOT performed.**

| Turn | Bound | Status | Phase completion |
|---|---|---|---:|
| 1 | 129 Physical reference evidence boundary | **ACCEPTED (synthetic)** | **12.5%** |
| 2 | 130 Reference instrument provenance and traceability | Planned | 12.5% |
| 3 | 131 Bounded reference uncertainty certificate | Planned | 12.5% |
| 4 | 132 Device response regularity test | Planned | 12.5% |
| 5 | 133 Probe insertion and same-path verification | Planned | 12.5% |
| 6 | 134 Reference drift and recalibration economics | Planned | 12.5% |
| 7 | 135 Unseen independent instrument stress | Planned | 12.5% |
| 8 | 136 Integrated empirical-gate freeze | Planned | 12.5% |

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
