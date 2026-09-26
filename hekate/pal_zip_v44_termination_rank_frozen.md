# PAL-ZIP v44 — TERMINATION RANK / NO-CYCLE MEASURE — FROZEN

**Parent:** PAL-ZIP v43  
**State:** FROZEN / 0e  
**Scope:** explicit monotone measure for recursive authority-state transitions.

## Target

v43 proved termination from finite-set shrinkage.

v44 freezes that argument as an explicit machine-checkable rank:

```text
RANK
::
|ELIGIBLE|
```

Every permitted transition from an active state must do exactly one of:

```text
1. reduce RANK
2. close one clean branch
3. halt
```

No permitted transition may keep the machine ACTIVE at the same or higher rank.

## Frozen transition law

```text
ACTIVE -> ACTIVE
::
RANK_after < RANK_before
```

while terminal transitions are:

```text
ACTIVE -> CLOSED
```

or:

```text
ACTIVE -> HALTED
```

A quarantine transition always removes at least one currently eligible identity, including
when that quarantine itself causes the halt.

## Frozen geometry

```text
eligible identities
::
T0 T1 T2

threshold
::
2
```

Active states are exactly the subsets whose rank is at least `2`.

## Exhaustive certification

- active states: 4
- quarantine transitions tested: 16
- active->active transitions: 3
- active->active non-decreasing transitions: 0
- active->halt quarantine transitions: 13
- halt transitions with bad rank decrease: 0
- close-branch transitions: 4
- close-branch terminal failures: 0
- explicit halt transitions: 4
- explicit halt terminal failures: 0
- empty-quarantine attacks: 4
- empty-quarantine false accepts: 0
- outside-identity attacks: 4
- outside-identity false accepts: 0
- duplicate-identity attacks: 4
- duplicate-identity false accepts: 0
- cycle-search start states: 4
- cycles found: 0
- maximum ACTIVE->ACTIVE path length: 1

**RESULT: 0e / PASS**

## Frozen no-cycle invariant

```text
ACTIVE
+
same rank
::
NO TRANSITION
```

Therefore any ACTIVE path has strictly descending natural-number rank:

```text
3 -> 2
```

and cannot return to an earlier active state.

For the frozen `3 identities / threshold 2` geometry:

```text
maximum ACTIVE->ACTIVE path length
::
1
```

After that the machine must either:

```text
CLOSE
```

or:

```text
HALT
```

## General invariant

For any finite eligible set:

```text
RANK := |ELIGIBLE|
```

is a well-founded natural-number measure.

If every nonterminal transition strictly decreases that rank, cycles are impossible.

```text
NO-CYCLE
::
monotone rank decrease
+
terminal close/halt
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
