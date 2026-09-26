# PAL-ZIP v13 — MIXED-EPOCH VOTE-SPLICING REJECTION — FROZEN

**Parent:** PAL-ZIP v12  
**State:** FROZEN / 0e  
**Scope:** formal quorum-context integrity.

## Target

Reject a synthetic quorum assembled from individually legitimate voters whose approvals came from different history heads.

Example attack:

```text
G0 approves MERGE2 at H10
G1 approves MERGE2 at H10
G2 approved the same MERGE2 at H07

naive count
::
3 approvals

correct contextual count at H10
::
2 approvals
```

## Frozen rule

A vote counts only when all of these match:

```text
eligible voter
exact merge
exact prior head
valid decision token
```

Therefore votes from distinct epochs cannot be spliced into one quorum.

## Certification

- current heads tested: 12
- all-current positive-control sets: 48
- all-current accepts: 48
- all-current failures: 0
- mixed-epoch vote sets tested: 2,160
- mixed-epoch false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
3 VALID IDENTITIES
!=
3 VALID VOTES FOR THIS STATE
```

The context is part of the vote.

```text
VOTE
::
voter
+
merge
+
prior_head
+
decision
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
