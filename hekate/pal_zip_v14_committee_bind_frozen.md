# PAL-ZIP v14 — COMMITTEE / CONFIGURATION BIND — FROZEN

**Parent:** PAL-ZIP v13  
**State:** FROZEN / 0e  
**Scope:** formal authority-set context.

## Target

Prevent votes issued under an old authority set from being counted after the eligible committee or threshold changes.

## Frozen committee identity

```text
COMMITTEE
::
sorted unique member identities
+
threshold
```

The order used to list members is not meaningful, but membership and threshold are.

## Vote context

```text
VOTE
::
voter
+
merge
+
prior_head
+
committee_anchor
+
decision
```

A vote counts only for the exact committee configuration under which it was issued.

## Certification

- committee permutation tests: 24
- permutation failures: 0
- member replacement changed anchor: 1
- threshold change changed anchor: 1
- new-committee positive controls: 4
- positive-control failures: 0
- old-committee replay tests: 1
- old-committee false accepts: 0
- mixed-committee splice tests: 15
- mixed-committee false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
SAME VOTER
+
SAME MERGE
+
SAME PRIOR HEAD

but

DIFFERENT COMMITTEE CONFIG
::
DIFFERENT AUTHORIZATION CONTEXT
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
