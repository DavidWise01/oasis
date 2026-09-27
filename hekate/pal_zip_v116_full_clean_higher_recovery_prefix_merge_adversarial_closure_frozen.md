# PAL-ZIP v116 — FULL CLEAN HIGHER-RECOVERY PREFIX-MERGE ADVERSARIAL CLOSURE — FROZEN

**Parent:** PAL-ZIP v115  
**State:** FROZEN / 0e  
**Scope:** exhaustive finite-state closure of the frozen `3 member / 2-of-3` clean higher-recovery prefix-merge system under conflicting authorization, quarantine, recovery, replay, tamper, and provenance attacks.

## Why v116 jumps to the hard target

Instead of adding one more local lemma, v116 closes the whole currently frozen state machine.

It model-checks every accepted conflict transition reachable from:

```text
members
::
T0 T1 T2

threshold
::
2 / 3

initial rank
::
3
```

until no accepted descendant remains.

This includes the recursive termination property that would otherwise have been the small v116 target.

## State

```text
CLEAN-HIGHER-RECOVERY-PREFIX-MERGE-STATE
::
eligible clean authority
+
quarantined authority
+
epoch
+
exact provenance head
+
ACTIVE / HALTED
```

## Accepted adversarial conflict step

Two independently valid clean merge authorizations exist in the same exact epoch:

```text
MERGE2(A,B)
MERGE2(A,C)
```

with threshold-valid quorums:

```text
Q_AB
Q_AC
```

The exact equivocation/quarantine set is:

```text
Q
=
Q_AB ∩ Q_AC
```

and the only accepted authority transition is:

```text
eligible'
=
eligible - Q
```

```text
quarantined'
=
quarantined ∪ Q
```

```text
rank'
<
rank
```

The original threshold remains fixed.

## Full geometry

From rank `3`:

```text
rank 3
├─ overlap 2 → rank 1 → HALTED
└─ overlap 1 → rank 2 → ACTIVE
                      └─ next conflict overlap 2
                           → rank 0
                           → HALTED
```

So the state machine has no accepted authority cycle.

No quarantined identity can re-enter.

No threshold weakening occurs.

## Provenance

Every accepted transition commits:

```text
exact previous head
+
exact conflict event
+
exact epoch
+
exact quorum pair
+
exact overlap
```

to a new provenance head.

Changing the previous head, parent context, epoch, quorum identity, or event changes provenance identity.

Identical future syntax appended to distinct provenance heads does not silently converge them.

## Certification

- reachable states: 16
- accepted transitions: 15
- terminal paths: 9
- maximum conflict rounds: 2
- rank-2 active states: 6
- halted states: 9
- strict-rank-decrease checks: 15
- strict-rank-decrease failures: 0
- quarantine-monotonicity checks: 15
- quarantine-monotonicity failures: 0
- no-reentry checks: 45
- no-reentry failures: 0
- threshold checks: 15
- threshold failures: 0
- exact-overlap checks: 15
- exact-overlap failures: 0
- provenance-binding checks: 15
- provenance-binding failures: 0
- cycle checks: 1
- cycle failures: 0
- terminal-extension attacks: 9
- terminal-extension false accepts: 0
- old-epoch replay attacks: 15
- old-epoch replay false accepts: 0
- parent-mutation attacks: 15
- parent mutations preserving identity: 0
- previous-head mutation attacks: 15
- previous-head mutations preserving identity: 0
- quorum-order tests: 60
- quorum-order failures: 0
- global provenance-head collisions: 0
- same-future divergence checks: 15
- same-future false convergence: 0

**RESULT: 0e / PASS**

## Frozen global invariants

```text
CONFLICT
::
exact overlap quarantine
```

```text
QUARANTINE
::
strict authority-rank decrease
```

```text
QUARANTINED IDENTITY
::
NO REENTRY
```

```text
rank < threshold
::
HALTED
```

```text
HALTED
::
NO ACCEPTED DESCENDANT
```

```text
OLD EPOCH
::
NO REPLAY
```

```text
DISTINCT PROVENANCE
+
IDENTICAL FUTURE SYNTAX
::
STILL DISTINCT
```

```text
UNRESOLVED CONFLICT
::
NO CANONICAL WINNER
```

## Boundary

This is exhaustive for the currently frozen finite authority geometry:

```text
3 members
2-of-3 threshold
two conflicting merge intents
append-only quarantine
fresh recovery epoch
```

It is not a proof for arbitrary `N`, arbitrary thresholds, or arbitrary dynamic membership.

That would require a parameterized theorem layer rather than finite-state exhaustion.

**STATUS: FROZEN / 0e / FULL CURRENT-LAYER ADVERSARIAL CLOSURE**
