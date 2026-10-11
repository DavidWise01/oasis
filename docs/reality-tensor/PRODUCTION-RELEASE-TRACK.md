# ROOT0 Production Release Track — PR-1

Status: **NOT PRODUCTION READY**. Supersedes the repeating P4.xx incremental gate roadmap. Historical P4.01–P4.67 remain archived experimental evidence, not release qualifications.

## Product boundary
One narrow product: an authenticated checkpoint authority with atomic monotonic CAS, durable anti-replay, signed policy and key rotation, TLS transport, and an independently operated append-only anchor. It is **not** distributed consensus, AI acceleration, or physical time dilation.

## Release train (no unbounded gate numbers)
| Phase | Deliverable | Exit evidence |
|---|---|---|
| R0 — Freeze | Choose single canonical implementation, dependency lock, threat model and supported runtime/OS; retire redundant prototypes | Reproducible fresh clone, architecture and version manifest |
| R1 — Build | Production service and operator CLI, health/readiness, configuration schema, structured audit logs, migration and backup/restore | Deterministic build and complete integration regression on clean clone |
| R2 — Security | Independent code review, least-privilege identities, secrets off repo, certificate/key rotation, replay lifecycle, secure bootstrap, strict admin authorization | Negative test matrix, rotation/revocation proof, vulnerability scan and review findings resolved |
| R3 — Independent anchor | Two separately administered hosts with distinct root/security administrators, independent keys and persistent storage | Signed primary rollback/fork exercises while remote anchor cannot be reset by primary admin; coherent rollback failure-mode documented |
| R4 — Resilience | Crash/power-cut testing, disk-full, timeout, network partition, restore/migration, failover, documented RPO/RTO, load soak | Published test records and observed recovery bound, no silent forks/data loss |
| R5 — Release certification | Green required CI on release commit, pinned release artifact + SBOM/provenance, deployment runbook, monitoring/alerts, external review | Release candidate approval with signed evidence and rollback plan |

## Hard no-go blockers
- No proven independently administered witness (currently only same-host and local HTTPS tests).
- No verified green hosted CI run on the exact release SHA.
- Runnable files have historically been in ZIP bundles rather than the GitHub source tree; clean-checkout reproducibility not independently established.
- No independently reviewed threat model, complete secret-custody procedure or production-safe bootstrap.
- No demonstrated network partition, power-loss, disk-full and recovery-time operating limits.
- No production CA/credential lifecycle or operator incident/rotation runbooks.

## Release acceptance contract
ALL R0–R5 exits must pass on the same pinned release candidate. Any missing evidence = NO-GO. Test counts alone and local PASS do not waive blockers. No arbitrary percentage increases; report phase `done / in progress / blocked`, critical blockers count, release decision, next concrete artifact. Prior 75% applies only to historical prototype milestone bookkeeping and must not be presented as production readiness.

## Immediate sprint: R0
1. Inventory GitHub and ZIP-only executables for P4.43–P4.67, select one canonical service, client, anchor and test harness.
2. Commit missing executable sources, checksums, fixtures and a deterministic package test command. Archive experiments without deleting provenance.
3. Produce signed-off architecture boundary, threat model and release requirements.
4. Demonstrate fresh-clone setup and documented PASS on supported clean Linux host.

## Decision
Current = **NO-GO / R0 in progress**. Production eligibility requires R0–R5, especially the independent host/CI evidence. This track ends in an explicit release decision instead of indefinitely advancing experimental gate numbers.
