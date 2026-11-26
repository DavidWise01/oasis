# AETHER Phase XIX — Independently Checked Execution Evidence and Custody Provenance

**AETHER-227-RS CONTENT-ADDRESSED CI EVIDENCE ZIP EXPORT & SAFETY VERIFIER COMMITTED. Phase XIX documentary software progress 3/8 = 37.5%. Native test execution, GitHub-hosted artifact retrieval and retention authentication: NOT VERIFIED. Authenticated external custodians: 0. Physical qualification: 0%. Operational ACT: HOLD.**

The [Phase XVIII freeze](224/decision.json) remains unchanged and records all eight documentary software milestones, without pretending historical Rust/Python execution, independent remote custody or physical-origin authentication was established. Phase XIX asks whether evidence of execution has been independently checked.

| Turn | Software milestone | Status | Progress |
|---|---|---|---:|
| 1 | 225 Native CI run/job/log/artifact source-revision reconciliation | **COMMITTED — actual CI outcome unverified** | **12.5%** |
| 2 | 226 Actual Actions run provenance and source-revision check | **COMMITTED — authenticated API probe source; live terminal run unverified** | **25%** |
| 3 | 227 Immutable evidence export and artifact content digest reconciliation | **COMMITTED — deterministic local ZIP, exact-byte inventory and hosted-artifact distinction** | **37.5%** |
| 4 | 228 GitHub execution-to-browser parity | Planned | 37.5% |
| 5 | 229 Independent source-ancestry test against owned mirrors | Planned | 37.5% |
| 6 | 230 External challenge and replay control | Planned | 37.5% |
| 7 | 231 Adversarial independently verified custody and CI evidence review | Planned | 37.5% |
| 8 | 232 Final Phase XIX documentary decision and freeze | Planned | 37.5% |

## AETHER-227-RS — Deterministic local artifact ZIP and exact-byte qualification

- [AETHER-227 ZIP verifier/exporter](227/archive_evidence.py) creates an exact-byte, sorted local ZIP of observed Rust compiler, regression, executable and qualification files with normalized metadata. It checks the ZIP archive and each entry SHA-256, required file presence, source commit consistency, AETHER-218 gate claims and AETHER-219 manifest HOLD fields. It rejects duplicate entry names, traversal/absolute paths, symlinks, oversized entries and corrupt archives without extracting them.
- [24 authored adversarial Python regressions](227/test_archive_evidence.py) exercise missing logs, corrupt ZIPs, swapped commits, counterfeit native qualification, altered manifests, unsafe paths, symlinks, archive substitution, exact digesting and deterministic repeat export. Test execution is **not independently confirmed**.
- The [GitHub Actions workflow](../.github/workflows/aether217-rust-qualification.yml) runs the synthetic ZIP regression tests and attempts a local `aether227-local-export.zip` and `aether227-local-inventory.json` prior to upload. The existing GitHub upload-artifact step remains separate, which may package the locally exported ZIP as a nested entry. **The locally built ZIP is not the GitHub-hosted Actions artifact ZIP**, and its matching content hashes cannot prove external retention.
- No actual GitHub-hosted ZIP was independently downloaded, read or SHA-256 verified in this turn, and no completed native Rust or Python CI result was observed. The verifier is published source—not a successful independent Actions acceptance run.
- [Animated 4D neon laboratory](227/) retains the 16-vertex/32-edge tesseract and shows synthetic archive failure conditions. [Protocol](227/protocol.json) records **Phase XIX 3/8 = 37.5%**, physical qualification **0%**, ACT **HOLD**. Sealed [Phase XVIII freeze](224/decision.json) is unchanged.
- **Next AETHER-228-RS:** host-delivered archive and browser display parity under an independently anchored digest/reference, without promoting self-hosted dashboard output to an independent witness. .dlw

## AETHER-226-RS — Authenticated Actions API run metadata readback

- [Read-only Actions provenance probe](226/actions_provenance.py) requests exact run, job and artifact metadata using GitHub's API and a token supplied through the environment. It pins expected source SHA, repository and workflow, checks run trigger and completed conclusion, matches the unique qualification job and its steps, and checks artifact ownership/expiration. It hashes exact decoded API response bytes. Missing, incomplete or contradictory evidence is **REJECT_OR_UNVERIFIED**.
- [26 authored mocked Python regressions](226/test_actions_provenance.py) cover bad run identity, source swap, foreign repository, incorrect workflow path, pending/failed jobs, incomplete API pagination, mismatched artifacts, failed steps, and missing API responses. **These fixtures are synthetic; no Python or native Rust test execution has been independently verified.**
- [Updated GitHub Actions workflow](../.github/workflows/aether217-rust-qualification.yml) grants `actions: read`, runs the synthetic regression suite, and uses the token to record its own run metadata as `aether226-api-readback.json` in the existing artifact upload. An in-progress workflow cannot observe its own terminal PASS, so missing terminal status remains explicitly unqualified. No token is embedded in the report.
- Current live run verification remains **UNVERIFIED**: public GitHub Actions and API pages could not be opened, and the connected PR-filtered workflow-run lookup is not a complete push/dispatch search. No actual terminal workflow run, runner log or artifact identity is claimed verified.
- [Neon 4D Pages laboratory](226/) retains the animated 16-vertex/32-edge shadow tesseract, with synthetic API discrepancy cases and a read-only view of [the published protocol](226/protocol.json). HTML publication is confirmed via GitHub source, not verified live Pages execution.
- **Phase XIX documentary progress 2/8 = 25%.** Independent external custodian control **0**, original hardware captures **0**, physical qualification **0%**, operational ACT **HOLD**. The [Phase XVIII freeze](224/decision.json) stays unchanged.
- **Next AETHER-227-RS:** exact action artifact content export and hash verification with run-bound evidence retention, while continuing to reject unauthenticated or absent CI evidence. `.dlw`

## AETHER-225-RS — Read-only execution evidence reconciliation

- [AETHER-225 Python reconciler](225/ci_reconciliation.py) checks claimed Actions run ID, exact pinned source revision, repository, completion status, trigger, unique qualification job, required step outcomes, nonexpired artifact associated with the same run, observed job-log bytes and source-bound native manifest bytes. Missing or contradictory evidence produces **REJECT**.
- [27 authored Python unit tests](225/test_ci_reconciliation.py) check source swaps, absent or failed runs, job/step failures, missing or modified artifacts, manifest mismatches, absent logs and false authority claims. **The fixtures are synthetic; authored tests are not independently verified as executed.**
- The [GitHub Actions workflow](../.github/workflows/aether217-rust-qualification.yml) includes AETHER-225 synthetic regressions. Publishing a workflow and adding a test does not authenticate a real runner or prove it passed.
- The connected GitHub status lookup for the last Phase XVIII commit `4a702452d99d9755259d86fed0e4260467b36870` returned **0 combined status checks** and **0 PR-associated workflow runs**. The workflow-run endpoint filters for pull requests and cannot rule out push/dispatch runs. The observation is **NO CONFIRMED CI CONCLUSION**, not PASS or FAIL.
- [Animated neon 4D lab](225/) retains the 16-vertex/32-edge tesseract and includes synthetic CI discrepancy cases. It reads [the protocol](225/protocol.json) but does not call GitHub Actions or execute Rust.
- The verifier cannot authenticate the origins of JSON records supplied to it, even if those records match. A real API readback, actual job logs and artifact bytes are still prerequisites for independent execution qualification.
- **Physical qualification 0% · Original hardware captures 0 · Independently authenticated custodians 0 · Operational ACT HOLD.**
- **Next AETHER-226-RS:** authenticated actual-run provenance and readback across supported GitHub APIs; preserve missing-run uncertainty instead of fabricating successful execution. .dlw
