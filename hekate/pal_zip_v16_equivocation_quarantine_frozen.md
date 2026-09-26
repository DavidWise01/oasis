# PAL-ZIP v16 — EQUIVOCATION QUARANTINE / PRESERVE EVIDENCE — FROZEN

**Parent:** PAL-ZIP v15  
**State:** FROZEN / 0e  
**Scope:** formal authority filtering after contradictory approvals.

## Target

When one identity approves two conflicting merges in the **same authority context**:

```text
same voter
same prior head
same committee
approve MERGE:A
approve MERGE:B
```

do not delete either vote.

Instead:

```text
PRESERVE BOTH AS EVIDENCE
+
QUARANTINE THAT VOTER'S AUTHORITY
FOR THIS DECISION CONTEXT
```

## Frozen rule

```text
equivocator
::
same voter
+
same prior_head
+
same committee
+
approve more than one distinct merge
```

The quarantine set is a **derived authority view**. It does not rewrite the evidence history.

```text
HISTORY
::
unchanged

AUTHORITY VIEW
::
exclude equivocators
for the current decision context
```

## Certification

For every pair of distinct 3-of-4 quorums over four voters:

- conflicting quorum pairs: 6
- exact equivocation sets: 6
- equivocation-set errors: 0
- evidence histories preserved: 6
- evidence-history mutations: 0
- MERGE:A still accepted after quarantine: 0
- MERGE:B still accepted after quarantine: 0

Positive/context controls:

- ordinary single-quorum controls: 4
- false quarantines on ordinary quorum: 0
- different-head / different-committee isolation tests: 8
- context-isolation failures: 0

**RESULT: 0e / PASS**

## Important consequence

For the frozen 3-of-4 / four-member geometry:

```text
conflicting 3/4 certificates
::
intersection >= 2
```

Quarantining the equivocating intersection leaves at most two unquarantined voters.

Therefore neither conflicting merge retains a 3-of-4 authorization.

This is a **safety result**, not a liveness result.

```text
v16
::
stops contradictory authority

v16
!=
choose a winner

v16
!=
restore quorum automatically
```

## No history erasure

```text
SLASH / QUARANTINE
::
authority consequence

NOT
::
evidence deletion
```

Both contradictory votes remain in the append-only provenance as the evidence that caused quarantine.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
