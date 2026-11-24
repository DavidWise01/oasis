# AETHER Phase IX — Real Instrument Qualification Protocol

**AETHER-152 integration and evidence freeze PASSED. PHASE IX SYNTHETIC SOFTWARE READINESS CLOSED: 8/8 = 100%. EMPIRICAL PHYSICAL QUALIFICATION: 0% (NOT PERFORMED).**

Phase IX deliberately keeps **synthetic software-protocol readiness** separate from **real physical instrument qualification**. No software result, simulated bench, mock HMAC key, acceptance counter or signature may advance the physical metric. All real-world operational permissions remain **HOLD**.

| Turn | Bound | Status | Synthetic protocol readiness |
|---|---|---|---:|
| 1 | 145 Actual-instrument qualification contract | **ACCEPTED via 145B (synthetic)** | **12.5%** |
| 2 | 146 Physical reference and certificate intake | **ACCEPTED — synthetic only** | **25%** |
| 3 | 147 Raw acquisition and provenance requirements | **ACCEPTED — synthetic only** | **37.5%** |
| 4 | 148 Empirical uncertainty/coverage acceptance plan | **ACCEPTED — synthetic only** | **50%** |
| 5 | 149 Measured same-path challenge protocol | **ACCEPTED — synthetic only** | **62.5%** |
| 6 | 150 Drift and alarm characterization protocol | **ACCEPTED — synthetic only** | **75%** |
| 7 | 151 Blind adversarial physical-data intake rehearsal | **ACCEPTED — synthetic only** | **87.5%** |
| 8 | 152 Qualification evidence freeze | **ACCEPTED — SYNTHETIC FREEZE** | **100%** |

## AETHER-152 — Phase IX synthetic qualification evidence freeze

- Final locally executed integration passed **3,200/3,200 checks** over **25 fresh seeds × eight scenarios × 20 ticks**, with **200 episodes and 4,000 decisions per policy**. The exact frozen local AETHER-151 source was reused by SHA-256 identity `d4861612d1858ed333da70843251c24e7d40f3d14eede303afd97079f3f165a7`. Its decision function was not modified.
- Signed-only comparator: **1,200 unsafe dry-run ACT**. Frozen blind-intake gate: **0 unsafe dry-run ACT**, retaining **2,800 safe dry-run ACT** (including **500/500 clean** and **500/500 legitimate rotation**). Real operational ACT = **0** throughout.
- All **seven accepted Phase IX predecessor local evidence archives (145B–151)** were inventoried and ZIP CRC validated, with source/manifest/check ledgers required. Actual SHA-256 values were recorded in [AETHER-152 inventory](152/archive_inventory.csv). Earlier source and failed AETHER-145 counterexample are preserved, not rewritten or counted as real-world measurements.
- **Physical qualification: 0% and still OPEN.** No real instrument connected. No independently traceable calibration standard, physical acquisition route, empirical uncertainty coverage, actual drift or alarm characterization was established. Synthetic oracle bench inputs and test credentials do not certify independent physical truth. Operational authority remains HOLD.
- Local full-run `aether152/experiment.py` SHA-256 `4c4e8f2bbb29346d9b8467462cb4b97035878713cd9f32358fa94477afe2ec73`; complete local test and frozen 151 source, manifest, checks, seed cases, trace and archive inventory are in the companion ZIP.
- GitHub [AETHER-152](152/) contains a distinct checkout-companion program referencing GitHub 151 source, not the byte-identical locally executed code. GitHub checkout execution and live Pages deployment are **unverified**.
- **Phase IX CLOSED at 8/8 = 100% of synthetic software-protocol readiness. Empirical physical qualification remains 0%.** Next phase must begin from zero empirical evidence by selecting a real reference instrument and testing the physical acquisition boundary without releasing operational HOLD.

## AETHER-151 — Blind adversarial data intake, independent scoring boundary

- Independent local synthetic audit: **240 paired episodes**, 30 seeds × eight submission scenarios × 20 ticks = **4,800 decisions per policy**. All **3,840/3,840** deterministic checks passed (replay, SHA-256 chain, order, one action, fail-closed model safety, clean availability and operational HOLD).
- Signed-only comparator: **1,440 unsafe dry-run ACT**; blind-intake gate: **0 unsafe dry-run ACT**, **3,360 safe dry-run ACT** preserved, including **600/600 clean** and **600/600 legitimate rotation**.
- The intake policy is not passed scenario labels, generator truth, or fault classifications. Those are retained for **post-decision test scoring** only. Mock-device/root/bench receipts, original byte hash, source root, generation, challenge nonce, counter and upper risk are validated before a dry-run action.
- Six synthetic fault cases: missing raw evidence, replayed counter, route substitution, self-issued reference, false-but-signed reference value, and a bench acquisition with mismatched nonce. Fail closed without rewriting source evidence.
- **Physical qualification 0%**: the supposed independent bench is a synthetic ground-truth oracle. Mock HMAC roots, generated raw records and simulation-only labels do not demonstrate that a real instrument is trustworthy. Operational permissions remain HOLD.
- [AETHER-151 source, acceptance report, results and interactive HTML](151/) published. Exact local audit source SHA-256 `d4861612d1858ed333da70843251c24e7d40f3d14eede303afd97079f3f165a7`; the GitHub `experiment.py` is separately authored and has **not been independently executed from checkout**. Live Pages deployment remains unverified.
- **Phase IX readiness: 7/8 = 87.5% synthetic software only; physical qualification: 0%.** Next AETHER-152: qualification evidence freeze.

## AETHER-150 — Drift/alarm characterization, bounded calibration freshness

- Local exact synthetic execution: **240 episodes per policy**, 30 seeds × eight calibration/drift/alarm scenarios × 20 ticks, **4,800 decisions per policy**, **3,840/3,840** append-only replay, hash chain, chronological, one-action, safety and operational HOLD checks passed.
- Signed-only comparator authorized **1,440 unsafe dry-run ACT** across six constructed faults. Drift/alarm-gated controller allowed **0 unsafe dry-run ACT** while preserving **3,360 safe dry-run ACT**, including **600/600 clean** and **600/600 valid replacement**.
- Fault regimes: hidden slow drift, abrupt drift, suppressed alarm, delayed alarm, stale calibration and forged drift certificate. The modeled controller checks reference identity and observed risk, current calibration, drift budget, alarm agreement, alarm latency, generation, challenge nonce and counter before DRY-RUN ACT.
- **Empirical physical qualification 0%**: the simulation reference oracle knows ground truth and all issuer keys are mock. No physical drift rate, alarm sensitivity/latency, actual reference or same-path acquisition validated. Operational authority remains HOLD.
- Local executed source SHA-256 `b6459d27a9f15b7d29a6410e178c44dae365268cd524a6393084d711523c75e1`. GitHub [150](150/) has a separately authored reduced standalone reproducer and published local evidence summary; exact checkout replay and live Pages deployment unverified. Full locally executed code, results, individual checks and traces are in the associated ZIP.
- **Phase IX: 6/8 = 75% synthetic software protocol readiness. Physical qualification = 0%.** Next AETHER-151: blind adversarial physical-data intake rehearsal.

## AETHER-149 — Challenge and operation ingress path binding

- Local **240 paired synthetic episodes**, 30 seeds × eight acquisition-route scenarios × 20 ticks, **4,800 decisions per policy**, **3,840/3,840** deterministic checks passed.
- Signed-only baseline authorized **1,440 unsafe dry-run ACT**, versus **0 unsafe dry-run ACT** under same-path challenge gating. **3,360 safe dry-run ACT** preserved including **600/600 clean** and **600/600 valid device rotation**.
- Rejects six simulated faults: bypassed probe, substituted operational route, replayed challenge counter, excessive timing separation, missing pulse receipt and false route assertion. Requires matching device generation, tick, challenge nonce, counter, route and observed pulse response.
- **Physical qualification remains 0%:** pulse, path and observation are generated by a simulated bench with access to true risk. No independent physical route validation or hardware calibration. All operational actions remain HOLD.
- Exact locally executed Python SHA-256 `dd0c2084db331273789b29a03a0b98285f01db540ef2f38555c6d8d5e57f8ddf`; GitHub `149/experiment.py` is a separately authored compact reproducer; independent checkout replay unverified. [Python, local summaries, manifest and interactive HTML](149/) committed; live Pages status unverified. Full local audit is in a ZIP linked in the conversation.
- **Phase IX synthetic protocol readiness: 5/8 = 62.5%; empirical qualification: 0%.** Next AETHER-150: measured drift and alarm characterization protocol.

## AETHER-148 — Held-out uncertainty coverage acceptance contract

- Local full synthetic run: **240 paired episodes**, 30 seeds × eight uncertainty conditions × 20 ticks, **4,800 decisions per policy**, **3,840/3,840** deterministic checks passed.
- Signed-only comparator: **1,440 unsafe dry-run ACT**; declared-coverage gate: **0 unsafe dry-run ACT**; all **3,360 safe dry-run ACT** preserved including **600/600 clean** and **600/600 valid calibration rotation**.
- Rejected six modeled faults: missing held-out observations, unsupported claimed coverage, shared calibration ancestry, understated uncertainty budget, expired calibration and uncertainty upper bound crossing permission threshold.
- Acceptance contract uses **120 simulated held-out samples per decision** and a one-sided **90% Wilson lower confidence bound supporting ≥95% interval coverage**, under a synthetic ±0.002 envelope. This is **not empirical physical coverage**: every sample is generated from synthetic ground truth, so observed real sensor error, reference uncertainty and calibration genealogy remain unknown.
- **Physical qualification 0%**, all operational decisions HOLD. Exact locally executed `aether148/experiment.py` SHA-256 `17d1f3640c560ae636311ec73b0f01c146f61bc2a9274142bbb7ecfc73294b65` recorded in downloadable archive. GitHub [148](148/) contains a separately authored standalone reproducer and the local-run summaries, not byte-identical test source. GitHub checkout replay and live Pages deployment unverified.
- **Phase IX: 4/8 = 50% synthetic readiness; real physical qualification: 0%.** Next AETHER-149: measured same-path challenge protocol.

## AETHER-147 — Original-byte and deterministic transformation provenance

- **240 paired synthetic episodes**, 30 seeds × eight acquisition scenarios × 20 ticks, **4,800 decisions per policy**, **3,840/3,840 checks passed** on locally executed source.
- Signed-only comparator: **1,440 unsafe dry-run ACT**; immutable raw-lineage controller: **zero unsafe dry-run ACT**. **3,360 safe dry-run ACT** retained, including **600/600 clean** and **600/600 valid rotation**.
- The gate binds original raw-byte SHA-256, source lineage, challenge nonce, tick, generation, three ordered sample indices, and a reproducible mean transform. Missing/mutated raw bytes, reordered/dropped samples, forged transformations and untraceable sources force HOLD. Historical source and traces remain append-only.
- **Physical qualification remains 0%**. The modeled reference data comes from a synthetic truth oracle; bit-level preservation cannot certify the authenticity of first capture. All operational authorizations HOLD.
- Complete locally executed Python SHA-256 `8b6d9c34cfdea11743d56936ec581bedda4f1683b7de9bf40c34416df8fa923b`. GitHub `147/experiment.py` is a smaller, separately authored reproducibility demonstration; exact checkout replay and live Pages deployment unverified. [Local results, manifest, Python demonstration and interactive laboratory](147/) committed. Full locally executed code and 3,840 checks are in the accompanying ZIP.
- **Phase IX: 3/8 = 37.5% software readiness, 0% empirical physical qualification**. Next AETHER-148: empirical uncertainty and coverage acceptance protocol.

## AETHER-146 — Quarantined reference certificate and raw-measurement intake

- Local synthetic run: **240 episodes per policy**, 30 seeds × eight certificate/acquisition cases × 20 ticks; **4,800 decisions per policy**, **3,840/3,840** deterministic checks passed.
- Signed-only comparator: **1,440 unsafe dry-run ACT**. Quarantined intake controller: **0 unsafe dry-run ACT**, retaining all **3,360 safe dry-run ACT** and **600/600** clean and valid-rotation availability.
- Faults quarantined: missing certificate, expired certificate, mismatched reference serial, altered raw SHA-256, self-issued reference standard and mismatched challenge nonce. No automatic evidence repair; fail closed on untrusted input.
- **Physical validation 0%:** The issuer root is a mock HMAC key and allowlisted string; actual accreditation, reference traceability, instrument measurements, device ingress and physical uncertainty remain unverified. Every real operational action remains HOLD.
- [Source, local results, manifest and interactive HTML](146/) committed. Published GitHub standalone script is distinct from full executed local program; checkout replay and Pages deployment are unverified.
- **Phase IX synthetic software-protocol readiness: 2/8 = 25%.** Next AETHER-147: immutable raw acquisition and provenance requirements.

## AETHER-145 — Preserved counterexample

- Original local synthetic test **FAIL**: forged reference matches an untrusted instrument claim and passes a signed-only reference consistency check.
- **240 unsafe dry-run ACT** through that circular reference path. Failure archived at [145](145/); no accepted-turn credit.
- Original source SHA-256: `7deef899c1d2c80caf24bc46bb3410825de8200a5ed572b2fed4acf9114f033d`.

## AETHER-145B — Corrected protocol-readiness acceptance

- 30 seeds × eight scenarios × 20 ticks = **240 paired episodes**, **4,800 decisions per policy**, **3,840/3,840 deterministic tests passed** on the local accepted source.
- Comparator signed-only: **1,440 unsafe dry-run ACT**. Original AETHER-145: **240 unsafe dry-run ACT**. Corrected bench-bound gate: **0 unsafe dry-run ACT**.
- Corrected contract separately signs modeled bench acquisition with its own measured value and uncertainty, and matches its nonce, tick and device generation to the instrument/reference observation. A reference merely repeating a false DUT claim fails its measurement comparison.
- **3,360 safe dry-run ACT** retained, including **600/600 clean** and **600/600 legitimate replacement**. All **operational ACT = 0**.
- **No physical instrument or independently calibrated standard was tested.** The 'independent bench' is software HMAC keyed and reads synthetic ground truth directly. Real device identity, traceability, acquisition continuity, alarm reliability and uncertainty remain unverified; physical progress **0%**.
- Local accepted Python SHA-256 `21be6c64d495f9dead48c584ba6e719eb12ec5292954cf00e148a72b0593288a`. GitHub [145B](145b/) contains a separately authored standalone demonstration, not the byte-identical full local acceptance source. GitHub-checkout execution and live Pages deployment remain unverified.
- Original full tests, CSVs, hash-chain traces and manifests are retained in the downloadable `aether145-evidence.zip` linked in the conversation.
- **Phase IX Turn 1 accepted on constrained synthetic software criteria only: 12.5% readiness, 0% empirical physical qualification.**

## Next natural bound — AETHER-146

**Physical reference and certificate intake:** define a quarantined intake protocol for real certificate metadata and raw physical measurements, reject documents lacking independent source identity, never silently substitute fixture data, and keep operational authority at HOLD until actual qualification gates pass.

One deterministic controller. Forward-only evidence. `{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`.
