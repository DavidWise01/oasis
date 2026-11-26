# AETHER Phase XX — Observed Execution Evidence Acquisition and External Provenance

**AETHER-233-RS LIVE GITHUB ACTIONS LOG & ARTIFACT ACQUISITION PROBE COMMITTED. Phase XX documentary source progress 1/8 = 12.5%. Confirmed terminal CI execution and independent runner provenance: UNVERIFIED. Original hardware captures: 0. Physical qualification: 0%. Operational ACT: HOLD.**

The [Phase XIX documentary freeze](232/decision.json) and earlier [Phase XVIII freeze](224/decision.json) remain unchanged. The newly authored code is a read-only acquisition attempt, not a claim that CI or native Rust has passed.

| Turn | Milestone | Status | Documentary progress |
|---|---|---|---:|
| 1 | 233 Fetch real Actions run, job logs and hosted ZIP by API ID | **COMMITTED — source only; no completed run authenticated** | **12.5%** |
| 2 | 234 Post-completion GitHub Actions result reconciliation | Planned | 12.5% |
| 3 | 235 Actual hosted ZIP digest and nested entry provenance | Planned | 12.5% |
| 4 | 236 Independent CI execution evidence archival | Planned | 12.5% |
| 5 | 237 Third-party custody and source ancestry examination | Planned | 12.5% |
| 6 | 238 Out-of-band nonce and receipt acquisition | Planned | 12.5% |
| 7 | 239 Adversarial independent provenance review | Planned | 12.5% |
| 8 | 240 Phase XX documentary qualification decision and freeze | Planned | 12.5% |

## AETHER-233-RS — Live read-only GitHub Actions byte acquisition

- [Python acquisition tool](233/acquire_execution.py) accepts an explicit completed workflow run ID and pinned 40-hex source revision. It uses a token supplied by the environment to read actual GitHub REST run, qualification jobs and hosted artifact listings. When job and artifact IDs are obtainable, it tries to fetch their **actual log and archive byte streams** and hashes the bytes with SHA-256. Absent, still-running, failed, expired, incomplete or contradictory records remain **REJECT_OR_UNVERIFIED**.
- [27 authored mocked transport tests](233/test_acquire_execution.py) exercise real-run binding decisions and missing/failed job, step, log and ZIP observations. These synthetic test fixtures are **not** authenticated real Actions records, and test execution is **not independently confirmed**.
- The [GitHub Actions qualification workflow](../.github/workflows/aether217-rust-qualification.yml) now includes the mocked test suite and a pre-upload read-only report `aether233-preupload-readback.json`. Because that run is **still executing** and the hosted ZIP is **not yet uploaded**, its own report cannot establish a terminal workflow success or archived ZIP integrity.
- Available connected GitHub access to the inspected previous commit `9fa4635265f2abdf7b1be38889c0aaac8d55cd72` returned **0 combined status entries** and **0 PR-associated runs**. The latter lookup is PR-filtered, not an exhaustive listing of push or dispatch runs. [Observed access record](233/access-observation.json) therefore contains no completed run ID or fabricated log/ZIP digest; it does not assert that runs are absent.
- The [animated neon 4D laboratory](233/) preserves the 16-vertex/32-edge tesseract and shows mock failure cases and published status limitations; its browser does not possess an API token or independently execute the Python/Rust code.
- [Protocol](233/protocol.json) records **Phase XX 1/8 = 12.5% documentary source progress**. Independently authenticated external custodians **0**, original physical captures **0**, physical qualification **0%**, recovery and operational ACT **HOLD**.
- **Next AETHER-234-RS:** obtain a verified post-completion workflow result through independently executed authenticated API readback, without using a currently running job to attest to its own terminal outcome. `.dlw`
