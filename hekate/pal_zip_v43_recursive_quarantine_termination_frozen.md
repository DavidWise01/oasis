# PAL-ZIP v43 — RECURSIVE QUARANTINE TERMINATION — FROZEN

**Parent:** PAL-ZIP v42  
**State:** FROZEN / 0e  
**Scope:** prove recursive fork → quarantine → recovery cannot recycle the same authority forever.

## Target

v42 can produce a second quarantine during clean recovery.

v43 freezes the termination rule:

```text
each quarantine round
must remove
at least one currently eligible identity
```

and:

```text
once quarantined in this lineage
::
that identity cannot re-enter
the same lineage's eligible authority
```

## Frozen state transition

```text
ELIGIBLE_n
↓ quarantine Q_n
ELIGIBLE_(n+1)
=
ELIGIBLE_n - Q_n
```

with:

```text
Q_n != EMPTY
```

Therefore:

```text
|ELIGIBLE_(n+1)|
<
|ELIGIBLE_n|
```

for every valid quarantine step.

## Frozen parent geometry

```text
initial eligible authority
::
T0 T1 T2

threshold
::
2 / 3
```

Recovery may continue only while:

```text
|ELIGIBLE| >= 2
```

otherwise:

```text
SAFE HALT
```

## Exhaustive certification

- initial authority identities: 3
- frozen threshold: 2
- admissible quarantine paths tested: 13
- quarantine steps tested: 22
- non-decreasing steps: 0
- identity reuse attempts: 1
- identity reuse false accepts: 0
- terminal safe halts: 13
- nonterminal paths: 0
- maximum quarantine rounds observed: 2
- finite-set bound violations: 0
- duplicate-quarantine identity tests: 2
- duplicate-quarantine false accepts: 0

**RESULT: 0e / PASS**

## Frozen consequence

For this `3 identities / threshold 2` lineage:

```text
round 0
::
3 eligible

round 1
::
2 or fewer eligible

round 2
::
below threshold
::
SAFE HALT
```

So the recursive protection path cannot loop forever by recycling the same identities.

## General finite-set invariant

For any fixed finite eligible set:

```text
non-empty quarantine each round
+
no re-entry
::
strictly decreasing eligible cardinality
```

Therefore recursive quarantine terminates in at most:

```text
initial eligible identity count
```

quarantine rounds, and usually sooner when the threshold is greater than zero.

## Important boundary

v43 proves termination of the authority-state machine.

It does **not** select a winning branch.

```text
termination
!=
winner selection
```

The terminal state is either:

```text
one clean authorized branch
```

or:

```text
SAFE HALT
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
