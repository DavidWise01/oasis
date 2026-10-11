# OASIS v1.0 — Three-Track Control Model

**Status:** architectural alignment for frozen P0-RC0. This document does not change frozen source, bypass acceptance, or claim formal verification of a symbolic operator.

## Canonical symbolic expression

```text
{{[
  i:identity:isomorphic:intent
  ::/`u:consequence:harmony:resonance`/
  ``u.s.::creation:life:death:recycle:repeat::``
  //::
]}}
```

The original spelling/punctuation is retained as a mnemonic interface and a proposed design vocabulary. Precise parser semantics are not yet executable or security-certified.

## Exactly three control tracks

### T1 — i / Identity and intent
- Authenticate principal, agent, service, role and request.
- Bind a canonical intent to a committed WAL event, policy version, nonce and hash ancestry.
- Enforce authorization / least privilege before mutation.
- Evidence: signed intent, nonce, authorization decision, source hash, explicit deny record.
- Hard stop: unidentified actor, missing provenance, unsupported intent => deny/quarantine.

### T2 — u / Consequence and harmony
- Evaluate target and floor consequences against the intent and committed WAL.
- Require independently verifiable signed receipt and floor acknowledgement.
- Check monotonic generation, replay resistance, idempotence and safety invariants.
- “Harmony/resonance” are operationally defined as nonconflicting verified state between authority, floor and broker, not an assumed physical phenomenon.
- Evidence: signed target/floor receipts, broker decision, durable bound generation.
- Hard stop: mismatched hash, invalid signature, ambiguity, inconsistent generation => deny/quarantine.

### T3 — u.s. / Lifecycle
- States: CREATED -> LIVE -> RETIRED -> RECYCLED / successor CREATED.
- “death” is the controlled deactivation of an identity or instance, not deletion of forensic history.
- “recycle/repeat” means reusing a verified process pattern with a **new** immutable event/identity/nonce; NEVER replay or overwrite an old WAL transaction.
- Evidence: ordered state transitions, revocation/rotation, append-only audit, tombstones, successor binding.
- Hard stop: successor cannot inherit revoked credentials, replay old acknowledgements or mutate historical records.

## Alignment: six production gates, three tracks

| Gate | Primary track | Other track obligations |
|---|---|---|
| P0 source freeze/reproducibility | T1 | T3 immutable release identity |
| P1 trust and security | T1 | T2 signature/authorization validation |
| P2 failure safety | T2 | T3 recovery and quarantine |
| P3 deployment | T3 | T1 service identity and least privilege |
| P4 operations | T3 | T2 monitored consistency and restore |
| P5 acceptance | T1 + T2 + T3 | All three require evidence and operator sign-off |

## Minimal transaction state machine

```text
REQUEST -- T1 identity+intent --> AUTHORIZED / DENIED
AUTHORIZED -- original WAL prepare+commit --> COMMITTED / QUARANTINED
COMMITTED -- T2 target+floor evidence --> RECONCILABLE / QUARANTINED
RECONCILABLE -- broker CAS --> BOUND exactly once
BOUND -- T3 lifecycle transition --> ACTIVE / RETIRED
RETIRED -- new identity + nonce + WAL --> NEW CREATED (not replay)
```

Any unsupported transition fails closed and emits an audit event.

## Project governance
There are **three control tracks**; the previously approved P0-P5 acceptance gates remain **six finite milestones**. Do not create a fourth control track, reset the freeze, or restart the endless SHEET sequence. Keep blocker IDs under the related P0-P5 gate and report evidence, not arbitrary completion percentages.

**Next blocker:** P0-B01 import exact runtime source of RC0 into Git. Maintain MANIFEST.sha256 and complete test/trace linkage. Once all three P0 blockers are closed, review P0 gate acceptance.

**Gate status at alignment:** P0 in progress (3 blockers); P1-P5 not evaluated; 0/6 accepted.
