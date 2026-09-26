# PAL-ZIP v45 — RANK WITNESS / TRANSITION PROVENANCE — FROZEN

**Parent:** PAL-ZIP v44  
**State:** FROZEN / 0e  
**Scope:** bind the termination rank to exact transition provenance.

## Target

v44 freezes:

```text
RANK := |ELIGIBLE|
```

v45 makes every permitted transition auditable with an exact rank witness.

## Frozen witness

```text
RANK-WITNESS
::
pre_head
+
eligible_before
+
rank_before
+
action
+
action_payload
+
eligible_after
+
rank_after
+
status
```

The rank values are not trusted literals. Verification recomputes them from the eligible sets
and reconstructs the exact expected transition.

## Certification

- valid witnesses built: 24
- valid witness failures: 0
- quarantine witnesses: 16
- terminal witnesses: 8
- head-tamper tests: 16
- head-tamper false accepts: 0
- rank-before tamper tests: 16
- rank-before false accepts: 0
- rank-after tamper tests: 16
- rank-after false accepts: 0
- eligible-after tamper tests: 16
- eligible-after false accepts: 0
- status-tamper tests: 16
- status-tamper false accepts: 0
- action-tamper tests: 16
- action-tamper false accepts: 0
- canonical ordering tests: 114
- ordering failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
RANK CLAIM
!=
RANK PROOF
```

A valid witness must bind the exact:

```text
head
state before
action
state after
terminal/nonterminal status
```

and its rank values must equal the recomputed cardinalities.

Therefore the v44 no-cycle measure is now carried as transition provenance rather than an
unverified runtime annotation.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
