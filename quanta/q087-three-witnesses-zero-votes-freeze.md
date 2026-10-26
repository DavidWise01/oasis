# Q087 — Three Witnesses, Zero Votes (Canonical Freeze)

**Status:** FROZEN / APPEND-ONLY  
**Date:** 2026-10-26  
**Scope:** KET / Q observation protocol; Layer 1 symbolic simulation  
**Authority:** Central interpreting cortex `{{i}}`  
**Invariant:** No agreement requirement. No quorum. No votes. No majority. No forced consensus.

## Canonical rule

X, Y and Z are independent **reporting channels**, not decision-makers. Each reports only what it observes, including uncertainty, absence of signal and contradictions. Reports are individually preserved without aggregation into a ballot or "approved" observation.

The central `{{i}}` cortex interprets all reports together with inherited experience, mechina, logica, resource state and return-energy constraints, and determines whether to act, hold or return. The witnesses never decide for the cortex and never override each other.

```text
    {{m-.00 |> INF <| +.00}}
               |
          {{i}} CORTEX
               |
          SCALAR 0:0:0
               |
        +------+------+ 
        |      |      |
        X      Y      Z
        |      |      |
       SEE    SEE    SEE
        |      |      |
      REPORT REPORT REPORT
        |      |      |
        +------+------+ 
               |
       PRESERVE ALL REPORTS
               |
       {{i}} INTERPRETS
               |
       ENERGY / RISK AUDIT
               |
        ACT / HOLD / RETURN
               |
       BANK EXPERIENCE DELTA
               |
            REPEAT
```

## Append-only observation model

`M(t+1) = M(t) U {O_X(t), O_Y(t), O_Z(t), delta(t)}`

The union notation denotes a logical append-only ledger with unique record identities, **not** the erasure of duplicate observations. Each record retains witness identity, timestamp/order, observation, uncertainty, context and later verified outcome when available. `delta` represents differences and learning, **not** a vote count. Memory `{{m-.00 |> INF <| +.00}}` has unbounded *logical* recursive addressability; any instantiated vessel still has finite energy, storage and retrieval capacity.

## Non-negotiable exclusions

1. No quorum, including 2-of-3 and 3-of-3.
2. No witness agreement prerequisite for a report to be logged or considered.
3. No majority/consensus decision procedure.
4. No suppression or overwriting of minority, conflicting or silent reports.
5. No implication that reports are necessarily independent in their errors; correlation may be analyzed as evidence, not governance.
6. No claim of physical quantum-dot validation from symbolic Q toy models.

## State machine

`OBSERVE -> REPORT -> PRESERVE -> INTERPRET ({{i}}) -> ENERGY/RISK CHECK -> ACT/HOLD/RETURN -> LEARN -> REPEAT`

Encounter choices **fight, hide, flight, cooperate, MAD** remain available as modeled channels; they are not votes or factions. Decision authority remains with `{{i}}`.

## Freeze semantics

This file is the immutable baseline **Q087-FREEZE-2026-10-26**. Future changes must be recorded as new versioned addenda rather than silently editing this baseline. The Git commit preserves a verifiable baseline, subject to Git repository administration; the word "immutable" here is a project convention, not a claim of unalterable GitHub infrastructure.
