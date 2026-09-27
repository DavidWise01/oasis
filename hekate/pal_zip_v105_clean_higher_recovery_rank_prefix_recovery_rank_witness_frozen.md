# PAL-ZIP v105 — CLEAN HIGHER-RECOVERY RANK-PREFIX RECOVERY-RANK WITNESS — FROZEN

**Parent:** PAL-ZIP v104  
**State:** FROZEN / 0e  
**Scope:** every valid clean higher-recovery rank-prefix quarantine decrease must carry an exact recomputable witness.

## Target

v104 proves recursive termination by strict clean-authority rank decrease.

v105 upgrades every valid decrease from a claim into an exact proof object.

## Frozen witness

```text
CLEAN-HIGHER-RECOVERY-RANK-PREFIX-RECOVERY-RANK-WITNESS
::
prior_head
+
eligible_before
+
rank_before
+
quarantined_set
+
exact clean equivocation evidence
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

The verifier recomputes:

```text
eligible_after
=
eligible_before - quarantined_set
```

```text
rank_before
=
|eligible_before|
```

```text
rank_after
=
|eligible_after|
```

```text
rank_after < rank_before
```

and:

```text
status
=
ACTIVE iff rank_after >= 2
HALTED otherwise
```

The exact quarantine event and post-head are also recomputed from the same fields.

## Frozen distinction

```text
RANK CLAIM
!=
RANK PROOF
```

A naked statement such as:

```text
3 -> 2
```

is not sufficient.

The exact prior state, exact removed clean authority, exact evidence, exact resulting state, and exact post-head must all bind together.

## Certification

- terminal paths: 6
- unique transitions: 9
- valid witnesses: 9
- verification failures: 0
- prior-head tamper attacks: 9
- prior-head false accepts: 0
- eligible-before tamper attacks: 9
- eligible-before false accepts: 0
- rank-before tamper attacks: 9
- rank-before false accepts: 0
- quarantine tamper attacks: 9
- quarantine false accepts: 0
- evidence tamper attacks: 9
- evidence false accepts: 0
- event tamper attacks: 9
- event false accepts: 0
- eligible-after tamper attacks: 9
- eligible-after false accepts: 0
- rank-after tamper attacks: 9
- rank-after false accepts: 0
- status tamper attacks: 9
- status false accepts: 0
- post-head tamper attacks: 9
- post-head false accepts: 0
- witness tamper attacks: 9
- witness tamper false accepts: 0
- canonical-order tests: 66
- canonical-order failures: 0
- rank-claim-only controls: 9
- rank-claim-only false accepts: 0
- witness collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
STRICT CLEAN HIGHER-RECOVERY RANK-PREFIX AUTHORITY-RANK DECREASE
::
must carry exact recomputable witness
```

and:

```text
RANK CLAIM
!=
RANK PROOF
```

No winner is selected.

The witness proves state transition integrity only.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
