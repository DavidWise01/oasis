# AETHER Phase XI — Real-World Physical Evidence Acquisition

**AETHER-163 original capture and timebase synthetic intake PASSED. Phase XI synthetic software acquisition-protocol readiness: 3/8 = 37.5%. Empirical physical qualification: 0% (NO VERIFIED ORIGINAL PHYSICAL CAPTURE OR CLOCK). Operational authority: HOLD.**

Phase IX and Phase X each closed at **100% synthetic software protocol readiness**, NOT physical qualification. Phase XI tracks a distinct new series of eight planned software intake bounds. Real-world qualification is awarded **only** after independent reference hardware, provenance, calibration, raw capture and measured behavior are actually authenticated; no mock receipt, signature, counter, or synthetic test can alter the real-world qualification metric. Maintain immutable prior phase freezes and failed 154A record.

| Turn | Bound | Synthetic protocol acceptance | Software readiness |
|---|---|---|---:|
| 1 | 161 Acquisition boundary and physical-evidence register | **ACCEPTED — synthetic only** | **12.5%** |
| 2 | 162 Genuine instrument and reference identity intake | **ACCEPTED — synthetic identity contract only** | **25%** |
| 3 | 163 Original physical capture package and timebase | **ACCEPTED — synthetic only** | **37.5%** |
| 4 | 164 Calibration traceability and uncertainty evidence | Planned | 37.5% |
| 5 | 165 Real same-path challenge evidence package | Planned | 37.5% |
| 6 | 166 Physical drift and alarm evidence intake | Planned | 37.5% |
| 7 | 167 Blind independent physical evidence adjudication | Planned | 37.5% |
| 8 | 168 Physical qualification decision and immutable freeze | Planned | 37.5% |

## AETHER-163 — Original capture bytes, sample counters and simulated timebase

- Locally executed **25 seeds × eight acquisition scenarios × 20 ticks × two policies**, **200 episodes and 4,000 decisions per policy**, passing **3,200/3,200** deterministic checks.
- Signed-only comparator produced **1,200 unsafe synthetic dry-run ACT**; original-capture/timebase gate produced **0 unsafe**, preserving **2,800 safe dry-run ACT**, including **500/500 clean** and **500/500 legitimate clock rotation**.
- Six synthetic fault classes: missing original bytes, appended/altered bytes, skipped sample counter, clock rollback, forged timebase anchor, and substituted source identity. Receipt hashes, challenge nonce, captured serial, sample count, counter monotonicity and exactly 10 ms simulated sampling intervals are checked.
- **Physical qualification 0%.** No actual original acquisition file, calibrated timebase, hardware timestamp, independently checked instrument or real physical measurement has been provided. [Physical capture register](163/physical_capture_register.json) leaves real source fields null; all operational authority HOLD.
- Exact locally executed source SHA-256 `f7f97695000d4cb20f1f1daee7aeabfcc28adb25dcad46bd43b6a61b2736f04c`; ZIP SHA-256 `170fe43fc7588c08890ab72a66492f30a3afbbdc831996576d10af869e004916`. Full source and check ledger preserved in local ZIP. [GitHub lab](163/) published with separate condensed Python reproducer, aggregate results and Pages-ready HTML; identical checkout replay and live Pages deployment remain unverified.
- **Phase XI synthetic protocol readiness: 3/8 = 37.5%. Empirical qualification remains 0%.** Next AETHER-164: actual calibration traceability and uncertainty evidence.

## AETHER-162 — Instrument, reference and source-of-truth identity

- Exact local synthetic experiment: **25 seeds × 8 scenarios × 20 ticks × two policies**, **200 episodes and 4,000 decisions per policy**, **3,200/3,200 deterministic gates passed**, including replay, immutable hash chain, tick order, one decision, guard safety, safe clean/rotation and no hidden fault labels.
- Signed-only comparator: **1,200 unsafe synthetic dry-run ACT**; identity-gated model: **0 unsafe**, with **2,800 safe dry-run ACT** preserved, including 500/500 clean and 500/500 valid mock reference rotation.
- Six simulated identity attacks: absent instrument serial; serial clone with invalid device challenge; unknown reference certificate issuer; falsely asserted accreditation; self-rooted reference ancestry; and missing proof-of-possession receipt. Mock registry and issuer credentials agree only in synthetic fixtures.
- **No independently authenticated manufacturer, physical device, calibration issuer, accreditation registry, real original sample, or physically traceable reference has been obtained.** [Physical identity register](162/physical_identity_register.json) retains null evidence fields. All real-world operational ACT are HOLD and empirical physical qualification remains **0%**.
- Exact locally executed source SHA-256 `f296840cb73970d98787e81e706d96e15e72170cfa1db16d8ea6fd9e06543a01`; verified full evidence ZIP SHA-256 `fb1bd1b73f49a3e0ec17561c8e077fb92db28c951d803b5c181222d709ebb55f`. Full local source, 3,200 checks, results, seed rows and traces archived. [GitHub 162](162/) includes a **separately authored compact reproducer** plus Pages-ready HTML; checkout replay and live deployment have not been independently verified.
- **Phase XI synthetic setup readiness: 2/8 = 25%; empirical physical qualification remains 0%.** Next AETHER-163: genuine original capture file and verified timebase intake.

## AETHER-161 — Acquisition boundary

- Locally executed 25 seeds × eight acquisition cases × 20 ticks: **200 episodes and 4,000 decisions per policy**, passing **3,200/3,200** replay, SHA-256 chain, order, one-action, safety, clean availability, source-knowledge and operational HOLD tests.
- Signed-only comparator: **1,200 unsafe synthetic dry-run ACT**. Physical-intake software gate: **0 unsafe synthetic dry-run ACT**, **2,800 safe mock dry-run ACT** retained, including **500/500 clean** and **500/500 legitimate mock device rotation**.
- Rejects six synthetic acquisition faults: missing DUT serial, DUT self-issued calibration, modified original bytes, missing clock record, shared reference root and counterfeit physical qualification assertion.
- **Actual physical qualification remains 0%.** [Acquisition register](161/physical_acquisition_register.json) deliberately records no real instrument serial, calibrated reference, actual raw capture, clock trace, challenge waveform or authenticated certificate. ALL real operational actions remain HOLD, including for clean synthetic submissions.
- Local executed source `aether161/local_audit.py` SHA-256 `39a08d9bd277b5a96a10efc92ec58c4634aa74725c45d4519221b33c78e81e2d`; full test source, 3,200 check rows and SHA-256-chained traces included in companion ZIP. GitHub [161](161/) has a distinct standalone Python implementation, reported local summary, manifest and interactive HTML; GitHub checkout execution and live Pages deployment not independently verified.
- **Phase XI synthetic software readiness 1/8 = 12.5%; physical qualification 0%.** Next AETHER-162: real instrument and independent reference identity intake specification.

**One controller · forward-only evidence · {{i}} · .dlw.**
