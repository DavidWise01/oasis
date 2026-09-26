# PAL-ZIP v57 — MERGE-AUTHORITY RANK WITNESS — FROZEN

**Parent:** PAL-ZIP v56  
**State:** FROZEN / 0e  
**Scope:** bind every merge-authority rank decrease to the exact quarantine event that caused it.

## Target

v56 proves merge-equivocation handling terminates because every valid quarantine strictly
reduces eligible merge authority.

v57 freezes an exact witness for each decrease.

A claimed rank change is not trusted by itself.

## Frozen witness

```text
MERGE-AUTH-RANK-WITNESS
::
prior_head
+
eligible_before
+
rank_before
+
quarantined_set
+
exact quarantine evidence
+
exact MERGE-AUTH-QUARANTINE event
+
eligible_after
+
rank_after
+
status
+
post_head
```

The rank values are serialized for audit, but verification recomputes them from the exact
eligible sets.

## Frozen verification

A witness is valid only if:

```text
Q != EMPTY
Q subset_of eligible_before

eligible_after
=
eligible_before - Q

rank_before
=
|eligible_before|

rank_after
=
|eligible_after|

rank_after
<
rank_before
```

and:

```text
status = ACTIVE
iff rank_after >= 2

status = HALTED
iff rank_after < 2
```

The evidence map must bind exactly the quarantined identities, and the quarantine event plus
post-head are recomputed from the same data.

## Certification

- exhaustive v56 transitions witnessed: 9
- valid witnesses: 9
- valid witness failures: 0
- prior-head tamper attacks: 9
- false accepts: 0
- eligible-before tamper attacks: 9
- false accepts: 0
- quarantine-set tamper attacks: 9
- false accepts: 0
- evidence-ref tamper attacks: 9
- false accepts: 0
- eligible-after tamper attacks: 9
- false accepts: 0
- rank-before tamper attacks: 9
- false accepts: 0
- rank-after tamper attacks: 9
- false accepts: 0
- status tamper attacks: 9
- false accepts: 0
- event-detach attacks: 9
- false accepts: 0
- post-head tamper attacks: 9
- false accepts: 0
- witness-text tamper attacks: 9
- false accepts: 0
- canonical ordering tests: 66
- ordering failures: 0
- witness collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
RANK CLAIM
!=
RANK PROOF
```

and:

```text
MERGE-AUTH-RANK-WITNESS
::
exact cause
+
exact before state
+
exact after state
+
recomputed rank decrease
```

Therefore a valid decrease cannot be detached from the quarantine evidence and event that
actually produced it.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
