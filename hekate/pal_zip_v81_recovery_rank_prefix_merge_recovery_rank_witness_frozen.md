# PAL-ZIP v81 — RECOVERY-RANK PREFIX-MERGE RECOVERY RANK WITNESS — FROZEN

**Parent:** PAL-ZIP v80  
**State:** FROZEN / 0e  
**Scope:** bind each strict v80 clean-authority rank decrease to an auditable exact witness.

## Target

v80 proves:

```text
RECOVERY-RANK-PREFIX-MERGE-RECOVERY-RANK
::
|ELIGIBLE CLEAN AUTHORITY|
```

and every valid quarantine transition satisfies:

```text
rank_after < rank_before
```

v81 freezes the proof object for each transition.

## Frozen witness

```text
RECOVERY-RANK-PREFIX-MERGE-RECOVERY-RANK-WITNESS
::
prior_head
+
eligible_before
+
rank_before
+
quarantined_set
+
exact recovery-equivocation evidence
+
exact quarantine event
+
eligible_after
+
rank_after
+
status
+
post_head
```

The rank fields are claims.

The verifier recomputes:

```text
rank_before
=
|eligible_before|

eligible_after
=
eligible_before - quarantined_set

rank_after
=
|eligible_after|
```

and requires:

```text
rank_after < rank_before
```

It also recomputes the exact quarantine event and post-head.

## Frozen distinction

```text
RANK CLAIM
!=
RANK PROOF
```

A witness is valid only if all authority-state geometry recomputes exactly.

## Certification

- terminal paths: 6
- transitions: 9
- valid witnesses: 9
- verification failures: 0
- prior-head tamper attacks: 9
- false accepts: 0
- eligible-before tamper attacks: 9
- false accepts: 0
- rank-before tamper attacks: 9
- false accepts: 0
- quarantine tamper attacks: 9
- false accepts: 0
- evidence tamper attacks: 9
- false accepts: 0
- event tamper attacks: 9
- false accepts: 0
- eligible-after tamper attacks: 9
- false accepts: 0
- rank-after tamper attacks: 9
- false accepts: 0
- status tamper attacks: 9
- false accepts: 0
- post-head tamper attacks: 9
- false accepts: 0
- witness tamper attacks: 9
- false accepts: 0
- canonical ordering tests: 66
- ordering failures: 0
- rank-claim-only controls: 9
- false accepts: 0
- witness collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
STRICT HIGHER-RECOVERY AUTHORITY-RANK DECREASE
::
must carry
an exact recomputable witness
```

and:

```text
RANK CLAIM
!=
RANK PROOF
```

The witness proves the exact v80 transition.

It does not choose a winning recovery-prefix merge branch.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
