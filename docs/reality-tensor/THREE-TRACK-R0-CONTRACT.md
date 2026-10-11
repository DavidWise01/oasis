# ROOT0 R0 — Three-Track Canonical Architecture

Status: PROPOSED R0 CONTRACT / NOT PRODUCTION-CERTIFIED
Supersedes ambiguous multi-track prototype naming, but does not supersede the six production release acceptance phases R0–R5.

Canonical expression (symbolic, preserved verbatim):

```
{{[i:identity:isomorphic:intent ::/`u:consequence:harmony:resonance`/\`\`u.s.::creation:life:death:recycle:repeat::\`\`//::}}
```

## Exactly three logical tracks

| Track | Symbol | Engineering responsibility | Release evidence |
|---|---|---|---|
| 1. Intent / Identity | `i:identity:isomorphic:intent` | Identify caller, verify signed intent, bind deployment, action, policy epoch and nonce; canonicalize representation | Request-signature, role separation, policy, replay and canonical encoding tests |
| 2. Consequence / Witness | `u:consequence:harmony:resonance` | Atomic compare-and-swap, signed receipts, monotonic checkpoint, independent anchor comparison, conflict rejection | Transaction crash matrix; immutable history; rollback/fork tests across independent custody |
| 3. Lifecycle / Operations | `u.s.::creation:life:death:recycle:repeat` | Secure bootstrap, serving, credential retirement/revocation, nonce epoch rollover, recovery and deterministic redeployment | Deployment, safe cleanup, restart, restore, rotation, monitoring and operational runbooks |

All three tracks are part of ONE service boundary. They are NOT separate production branches or independent kernels. Repeat denotes repeating an authorized lifecycle event, NOT self-replicating agents, unbounded recursive execution or overwriting history.

## Fixed pipeline

```
INPUT
  |
  v
[1] IDENTITY / INTENT -- signature, policy, nonce, canonical semantics
  | authorized
  v
[2] CONSEQUENCE / WITNESS -- atomic CAS, signed checkpoint, external anchor
  | witnessed outcome
  v
[3] LIFECYCLE / OPERATIONS -- record, monitor, rotate, recover, retire
  | append-only successor (new authorized intent)
  +-------------------------------> [1]
```

## Fail-closed invariants

1. Invalid identity, signature, role, deployment, nonce or intent: no consequence.
2. A nonconsecutive or conflicting checkpoint is never committed.
3. Nonce consumption and local checkpoint publication commit atomically.
4. Policy/key retirement cannot reactivate retired credentials via an old epoch.
5. Successful publication is accepted as externally anchored only after independently authenticated receipt.
6. Missing, stale, contradictory or unavailable external witness = NO-GO for externally anchored acceptance.
7. Recycle means garbage-collect only retired nonces and temporary artifacts subject to durable epoch/policy proofs; never delete committed provenance.
8. Recovery must preserve ordering and report a detectable failure on rollback.
9. Creation, life, death, recycle and repeat are software lifecycle labels, not claims of biological life or physical identity equivalence.

## Alignment with fixed production phases

- R0 Freeze: select one canonical implementation with these three internal tracks, not additional tracks.
- R1 Build: package one deployable service and CLI with explicit contracts at each boundary.
- R2 Security: verify identity and policy plus revocation/replay defenses.
- R3 Independent anchor: establish separately administered storage for consequence witness.
- R4 Resilience: qualify the lifecycle from bootstrap to fault recovery and retirement.
- R5 Release: certify all three tracks together on one pinned release candidate.

Current release decision: **NO-GO**. R0 design semantics recorded; runnable implementation and clean-checkout proof still outstanding. Historical 75% refers solely to former prototype milestones, not production readiness.
