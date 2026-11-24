# AETHER Phase X — Physical Reference Acquisition Setup and Evidence Intake

**AETHER-160 local evidence freeze PASSED. PHASE X SYNTHETIC SOFTWARE SETUP READINESS CLOSED: 8/8 = 100%. EMPIRICAL PHYSICAL QUALIFICATION: 0% (NO INSTRUMENT, TRACEABLE CALIBRATION OR MEASURED SAMPLES). Operational authority: HOLD.**

Phase X distinguishes *software protocol development* from *actual independent reference equipment acquisition, calibration and measurements*. Passing the former cannot advance the latter. This ledger does not claim that any instrument is physically attached or any traceability certificate has been authenticated.

| Turn | Bound | Acceptance | Software setup readiness |
|---|---|---|---:|
| 1 | 153 Equipment register and commissioning contract | **ACCEPTED — synthetic only** | **12.5%** |
| 2 | 154 Independent reference identity and certificate intake | **ACCEPTED — synthetic corrected test** | **25%** |
| 3 | 155 Original physical-capture file and timing intake | **ACCEPTED — synthetic only** | **37.5%** |
| 4 | 156 Reference traceability and uncertainty budget | **ACCEPTED — synthetic only** | **50%** |
| 5 | 157 Same-path hardware challenge procedure | **ACCEPTED — synthetic only** | **62.5%** |
| 6 | 158 Physical drift/alarm acceptance thresholds | **ACCEPTED — synthetic only** | **75%** |
| 7 | 159 Unknown-fault blind physical intake rehearsal | **ACCEPTED — synthetic combined faults only** | **87.5%** |
| 8 | 160 Real-world qualification evidence decision freeze | **ACCEPTED — SYNTHETIC EVIDENCE FREEZE ONLY** | **100%** |

## AETHER-160 — Phase X synthetic evidence-freeze closure

- Exact locally executed program imported the **unmodified frozen AETHER-159** Python controller (source SHA-256 `c02f6aa6bf43b46b0b0e92fa5b604c05392c6a237b7d0cde3c971a9a13cb4f56`). It reran 25 **fresh** seeds × eight combined-fault scenarios × 20 ticks = **200 episodes and 4,000 decisions per policy**, passing **3,200/3,200 deterministic checks**.
- Signed-only comparator: **1,200 unsafe synthetic dry-run ACT**; frozen blind-intake gate: **zero unsafe synthetic dry-run ACT**, **2,800 safe synthetic dry-run ACT** retained (500 clean; 500 legitimate rotation). All physical operational permissions remained **HOLD**.
- Inspected and hashed all **seven predecessor local ZIPs AETHER-153–159**. Every archive passed CRC, contained its accepted manifest, exact executed source, results and **3,200/3,200** passing source check rows. The original **AETHER-154A FAIL** manifest is preserved. Earlier experiments were archived and audited, **not comprehensively rerun**.
- Final local source SHA-256 `d053b735efac8ddb19f3efcd7f06e8e22d0fd4b42bf6032151e3bcac8fd279ac`. The complete locally executed code, frozen source, checks, seed cases, SHA-256 chain samples, inventory, manifest and physical decision register are in the companion ZIP (SHA-256 `21bb35254464a81ad945813a1bf9633701a8a441372eb1157a5280771a31cd1b`).
- **Real physical qualification is OPEN at 0%.** No actual instrument, traceable independent reference, certified physical source, original instrument acquisition bytes, same-path pulse test, hardware drift or alarm timing was supplied or validated. [Physical qualification decision](160/physical_qualification_decision.json) retains explicit null values. No real operational ACT.
- The [GitHub AETHER-160](160/) Python is a separately authored checkout companion using GitHub 159 rather than the exact frozen local source. Matching GitHub checkout replay and live Pages deployment are **unverified**, although committed files can be checked by GitHub readback.
- **Phase X synthetic setup readiness is CLOSED: 8/8 = 100% software-only; empirical qualification remains 0%.** The next phase must collect and authenticate actual physical evidence without altering this freeze or prematurely lifting operational HOLD.

## AETHER-159 — Blind combined-fault intake and unknown-evidence quarantine

- Exact locally executed synthetic experiment: **25 seeds × eight scenarios × 20 ticks × two policies**, **200 episodes and 4,000 decisions per policy**, **3,200/3,200 checks PASS**. Tests include deterministic replay, SHA-256 append-only source chain, tick order, one decision per tick, modeled safety, clean availability and permanent operational HOLD.
- Signed-only comparator permitted **1,200 unsafe dry-run ACT**. Blind-intake gate permitted **0 unsafe dry-run ACT**, retained **2,800 safe dry-run ACT** including **500/500 clean** and **500/500 legitimate rotation**.
- Six simulated combined conditions: missing capture + alarm suppression; self-asserted reference issuer + route substitution; reference counter replay + delayed alarm; reference/bench contaminated together while original raw samples disagree; calibration expiry + suppressed alarm; and signed false reference measurement.
- Controller is never passed scenario labels, generator seed, or hidden truth. Test scoring is post-decision only. This is **limited software blindness**, not tested generalization to real unknown physical attacks or independent source roots.
- **Physical qualification remains 0%**: all signals and bench sources were generated from the same simulator and no authentic calibration, reference instrument or physical samples observed. [Physical evidence register](159/physical_blind_intake_register.json) retains explicit unknowns. Operational authority HOLD.
- Full locally executed Python SHA-256 `c02f6aa6bf43b46b0b0e92fa5b604c05392c6a237b7d0cde3c971a9a13cb4f56` and all checks, seed results and SHA-256 traces are in the downloadable ZIP. [GitHub experiment, results and interactive Pages-ready HTML](159/) committed; GitHub code is separately authored compact reproduction and checkout execution is unverified. Live Pages deployment unverified.
- **Phase X software protocol setup readiness 7/8 = 87.5%; empirical physical qualification 0%.** Next AETHER-160: final qualification evidence decision freeze, with real-world qualification gap explicitly OPEN.

## AETHER-158 — Synthetic drift and alarm acceptance, calibrated response protocol

- Locally executed 25 seeds × eight drift/alarm scenarios × 20 ticks, **200 episodes and 4,000 decisions per policy**. All **3,200/3,200 checks passed**, including replay, SHA-256 append-only ledger, tick order, one action, fail-closed model safety, clean availability and permanent real-world HOLD.
- Signed-only comparator authorized **1,200 unsafe dry-run ACT**. The drift/alarm gated controller authorized **0 unsafe dry-run ACT** while retaining **2,800 safe dry-run ACT** (500 clean, 500 legitimate device rotation).
- Six modeled faults: slow drift exceeding the declared threshold, abrupt drift, suppressed alarm, delayed alarm, stale drift receipt and forged baseline epoch. The software requires drift ≤.001/tick, a fresh baseline/expiry, matching mock alarm observations, latency ≤50 ms and risk bound below .025. These limits are simulation parameters **not empirical tolerances**.
- **Physical qualification remains 0%**. No real hardware alarms, sensor drift, calibrated reference, acquisition timing, or empirical detection performance was measured. [Physical alarm register](158/physical_alarm_register.json) remains empty; operational authority stays HOLD.
- Exact executed local audit source SHA-256 `f6ded480f5de2b82e1ed7e2ceb352016d7f63ab540183a53b9e6cdf5ae98de2e`, complete checks, seed results and traces packaged in companion evidence ZIP. [GitHub Python, local summaries, manifest, and interactive HTML](158/) committed. The GitHub script was **separately authored and has not been independently checkout-tested**, and live Pages deployment remains unverified.
- **Phase X synthetic software setup readiness: 6/8 = 75%; physical qualification 0%.** Next AETHER-159: blind unknown-fault physical-data intake rehearsal.

## AETHER-157 — Same-path challenge-pulse and hardware route intake

- Exact local synthetic run: **25 seeds × eight route/pulse scenarios × 20 ticks**, **200 paired episodes and 4,000 decisions per policy**, **3,200/3,200 deterministic checks passed**.
- Signed-only comparator authorized **1,200 unsafe dry-run ACT**; the route/challenge gate authorized **zero unsafe**, preserving **2,800 safe dry-run ACT**, including **500/500 clean** and **500/500 legitimate device rotation**. Operational action remained HOLD.
- Six constructed failures were quarantined: missing probe, bypassed pulse observation, substituted acquisition route, replayed pulse counter, excessive propagation delay and false coupling assertion. Mock nonce, device serial, generation, original raw hash, challenge amplitude and a maximum 50 ms propagation window must match.
- **Physical qualification 0%:** pulse, route and reference observations derive from one software fixture and cannot establish a real shared hardware path. [Physical path register](157/physical_path_register.json) remains uncommissioned and has no physical waveform, input route trace, reference certificate or hardware serial. Operational authority stays HOLD.
- Exact locally executed source SHA-256 `924bd012dbaba31647692a96744985935abbe09f7ef858abae2c67f3b529e82e`. [Interactive HTML, test demo, results and register](157/) published; GitHub Python is separately authored from local executed code, independent checkout replay and live Pages deployment unverified. ZIP evidence includes exact local code, full check ledger, sample traces and manifest.
- **Phase X synthetic setup readiness: 5/8 = 62.5%; empirical qualification: 0%.** Next AETHER-158: measured drift and alarm thresholds protocol.

## AETHER-156 — Calibration ancestry, RSS uncertainty and supported coverage

- Exact locally executed synthetic audit: **25 seeds × eight reference scenarios × 20 ticks**, 200 episodes and **4,000 decisions per policy**, **3,200/3,200** deterministic gates passed.
- Signed-only baseline authorized **1,200 unsafe dry-run ACT**. The reference traceability and uncertainty gate authorized **0 unsafe dry-run ACT** and preserved **2,800 safe dry-run ACT** (500/500 clean and 500/500 legitimate reference rotation). Operational ACT remained zero.
- Four required modeled standard uncertainty components: calibration, repeatability, resolution and drift. Combined uncertainty is RSS, expanded with **k=2**; the gate checks a one-sided **90% Wilson lower bound of at least 95%** from 120 simulated held-out samples and rejects bounds crossing the permission threshold.
- Six modeled faults: missing uncertainty contributor, shared calibration ancestry, understated resolution, expired calibration, unsupported coverage, and reference value contradicting a modeled bench. All failures HOLD without rewriting previous evidence.
- **Physical qualification remains 0%**: reference and bench are synthetic oracle/fixtures. No actual accredited lab, calibration ancestry, traceable equipment, real uncertainty contributors, independent measurements, or physical uncertainty coverage were validated. [Physical uncertainty register](156/physical_uncertainty_register.json) retains null values and zero measured samples.
- Locally executed source SHA-256 `05a2bd83fa637c3030fc284384f92c406e99f66db3bcefe96139ee7d3a400db8`. [GitHub lab and evidence summary](156/) are committed; the GitHub Python demo is separately authored from the exact local source, checkout replay unverified. Live Pages deployment unverified. Full local source and 3,200 checks are in the evidence ZIP.
- **Phase X software protocol setup readiness: 4/8 = 50%; empirical physical qualification: 0%.** Next AETHER-157: same-path hardware challenge protocol.

## AETHER-155 — Immutable raw-capture bytes and monotonic sample timing

- Local exact synthetic run: **25 seeds × eight conditions × 20 ticks**, **200 episodes and 4,000 decisions per policy**, **3,200/3,200** checks passed for deterministic replay, hash chaining, order, one decision, modeled safety, preserved safe cases and permanent operational HOLD.
- The signed-only comparator admitted **1,200 unsafe dry-run ACT**; the original-byte/timing gate admitted **0 unsafe**, retaining **2,800 safe dry-run ACT**, including **500/500 clean** and **500/500 legitimate clock rotation**.
- Six constructed failures: missing raw capture, appended/modified bytes, sample counter gap, clock rollback, forged timestamp origin and captured reference identity substitution. The source byte hash, challenge nonce, signed generation, counter sequence, declared sample interval and source identity must agree.
- **Physical qualification remains 0%**. The original bytes and absolute clock are synthetic, no actual instrument/timebase was observed, and all real operational permissions remain HOLD. [Blank physical-capture register](155/physical_capture_register.json) retains missing physical metadata.
- Exact locally executed Python SHA-256 `8b5a4310b2f78031ba06f8fbe148b1a05417257194bff4ea9103f3cba3831a61`. [AETHER-155 source, results, acceptance manifest and interactive lab](155/) published; GitHub source is separately authored from the local test, and independent GitHub checkout replay and live Pages status are unverified. Full locally executed audit is available in the companion ZIP.
- **Phase X setup readiness 3/8 = 37.5% synthetic; empirical qualification = 0%.** Next AETHER-156: traceability and uncertainty budget intake.

## AETHER-154 — Quarantined reference-issuer identity and calibration certificate intake

- Local corrected software test: **25 seeds × eight scenarios × 20 ticks = 200 episodes per policy, 4,000 decisions per policy**, with **3,200/3,200 deterministic gates passed**.
- Baseline signed-only comparator: **1,200 unsafe dry-run ACT**; the certificate intake gate: **0 unsafe dry-run ACT**, retaining **2,800 safe dry-run ACT** including **500/500 clean** and **500/500 valid reference rotation**.
- Tested six synthetic certificate failures: missing issuer identity, unrecognized issuer credential, serial mismatch, expired certificate, broken claimed source ancestry and altered signed uncertainty. The intake policy uses signed mock certificate plus raw record and separate mock bench; no hidden test labels passed into authorization.
- **Preserved initial failure AETHER-154A:** **400/400 hash-chain verifications failed** because the writer hashed the previous digest field but the verifier omitted it. Corrected 154 fixed the verifier's reconstruction only; the authorization gate remained unchanged. The original and corrected sources, checks, manifests and traces are in the ZIP. [Original failure record](154a/failure.json).
- **Physical qualification 0%**: the actual equipment/certificate [register](154/physical_reference_register.json) remains null. No accredited laboratory issuer, calibrated standard, physical measurement or real reference acquisition verified; all operational actions **HOLD**.
- Exact corrected local executed Python SHA-256 `c40bf52d6a1b5ed5068d6e6967d2d25130b16cee9a62963dd354f675747e9fc7`; GitHub [154](154/) includes separately authored standalone reproducer, numerical results, manifest, neon interactive HTML and uncommissioned register. Independent checkout replay and live Pages deployment remain unverified.
- **Phase X synthetic setup-readiness: 2/8 = 25%; empirical qualification: 0%.** Next AETHER-155: original physical-capture file and timing intake.

## AETHER-153 — Physical-reference acquisition setup boundary

- Exact local synthetic execution: 25 seeds × eight cases × 20 ticks = **200 paired episodes, 4,000 decisions per policy**, **3,200/3,200** deterministic acceptance checks.
- Baseline signed-only: **1,200 unsafe dry-run ACT**. The setup-gated controller: **zero unsafe dry-run ACT**, **2,800 safe dry-run ACT** retained, including **500/500 clean** and **500/500 reference rotation**.
- Six constructed faults were quarantined: missing reference serial, untrusted lab, expired calibration, missing raw capture, unverified route and challenge mismatch.
- An explicitly *uncommissioned* [equipment register](153/physical_setup_register.json) leaves serials, certificate provenance, calibration dates, actual measurement data, reference acquisition route and uncertainty blank. No hardware was connected or independently measured; **physical qualification remains 0%**. All operational ACT remain HOLD.
- Exact locally executed source SHA-256 `e61bcff26a003ae570a8279b57f45709e15fabb42cd1ad285a250db14e9a069b`; source plus 3,200 checks, seed results, traces and manifest preserved in locally generated ZIP.
- [GitHub AETHER-153 source, results, manifest, interactive HTML](153/) are committed. The GitHub Python is separately authored (not byte-identical to the local run); independent checkout replay and live Pages deployment remain unverified.

## Next AETHER-154

Define quarantined intake for actual reference instrument identity and calibration certificate credentials, retain nil values when unknown and forbid importing simulated fixture assertions as measured physical evidence.

One controller. Forward-only evidence. `{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`.
