# OASIS v1.0 — Production Qualification Charter

**Baseline:** SHEET 247 (process-crash recovery and local transport simulations). SHEET numbering is **frozen**. Future work is tracked as P0–P5 release gates and blockers (e.g. P1-B03), not new SHEET numbers.

## Outcome and scope
Ship one explicitly defined OASIS protected WAL + signed target/floor recovery service as a versioned, reproducibly built and operable deployment. The S176 original Node writer, Python broker, local SQLite and mTLS target/floor form the candidate. Security claims are limited to measured deployment/fault models. No claim of atomic cross-store transaction, hardware durability or partition tolerance without independent proof.

## Production gates — all mandatory

| Gate | Acceptance artifact | Exit evidence |
|---|---|---|
| P0 Source and reproducible release | Immutable release tag, complete runtime source in Git, lockfiles/SBOM, build script and hashes, service/process diagram | Fresh clean checkout reproduces artifact; complete source and third-party licenses inventoried; no hardcoded fixture keys or hidden ZIP-only source |
| P1 Security and trust | Threat model, authz matrix, peer credential policy, TLS PKI/rotation and secrets model, static/dependency scanning, adversarial tests | No unmitigated critical/high findings; test rejects unauthorized clients, replay, forged signatures and same-host privilege escalation within declared threat model; documented key rotation |
| P2 Failure safety | Written crash/partition/retry fault matrix; independent-host setup; recovery invariants and logs | Every in-scope fault has reproducible evidence for unchanged committed ancestry, no invented commit/ACK, monotonic and unique generation; all unknown outcomes quarantined; demonstrated clean restart; power-cut durability must be explicitly tested before claiming |
| P3 Deployment | Container or systemd package; declarative config, resource limits, health/readiness probes, install/upgrade and rollback | Fresh non-dev machine install passes smoke suite, with least privilege, restart persistence and clean rollback |
| P4 Operations | Metrics/structured audit, SLOs, dashboards/alerts, backup, restore, capacity and incident playbook | Measured restore drill with hashes/keys verified; rotation and failure alerts demonstrated; recovery time and data-loss objectives declared and measured |
| P5 Production acceptance | Signed release, evidence index, residual-risk register and go/no-go decision | P0-P4 signed off, release install and rollback drill witnessed, no open release blockers; scoped approval by operator |

## Invariants
1. WAL entry identity and hash ancestry never change silently.
2. Prepare-only is never promoted to committed.
3. Target/floor signature and exact committed WAL ancestry required for a repair.
4. One monotonically advancing floor generation per authorized repair; retry idempotence.
5. Ambiguous delivery, inaccessible peer or undecidable state -> fail closed/quarantine, not optimistic success.
6. Signed evidence, decisions and repair actions have audit provenance.

## Metrics and stop rules
**Production readiness = gates accepted / 6. Initial status: 0/6.** Historical 90% was local engineering coverage and is deprecated. Do not move a gate to PASS using simulation if its acceptance criterion explicitly requires independent hosts, power loss or another real condition. Each iteration must close a named blocker with exact tests/evidence, or explicitly record a blocker. Once P5 accepts, release v1.0; stop feature expansion. Post-release changes require security patches/observed incidents or separately approved scope.

## First work item P0-B01
Consolidate canonical source from ZIP-only SHEET 247 and ancestors into Git; map executable services; remove archived test fixtures from production paths; provide one clean-checkout build/test invocation. Do not issue a release-readiness claim until this is done.

## Honest baseline
Local executed SHEET 247 assertions: 75/75 across three suites, but no independent host partition, hardware power-cut, production credential lifecycle, SBOM, clean-checkout proof, deployment recipe, operational backup-restore drill or signoff yet.
