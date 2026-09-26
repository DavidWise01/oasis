# PAL-ZIP v39 — CERTIFIED POLICY-ROTATION FORK — FROZEN

**Parent:** PAL-ZIP v38  
**State:** FROZEN / 0e  
**Scope:** conflicting authorized policy rotations from the same pre-rotation head.

## Target

Test the case where the current parent policy legitimately authorizes two different children
from the exact same pre-rotation head.

For the frozen test geometry:

```text
parent
::
P2 = 2 / 3

children
::
P1 = 1 / 3
P3 = 3 / 3
```

Both branches may individually possess valid `ROTATION-CERT`s.

That does **not** make either child canonical.

## Fork geometry

```text
HEAD H0
  |
  +---- AUTHORIZED-ROTATION(P2 -> P1)
  |
  +---- AUTHORIZED-ROTATION(P2 -> P3)
```

The two branch heads remain distinct.

Appending the same later payload does not erase the fork.

## Rotation-equivocation rule

```text
same voter
+
same pre_head
+
same parent_policy
+
approve child A
+
approve child B
+
A != B
::
ROTATION EQUIVOCATION
```

With a `2 / 3` parent policy, any two valid 2-of-3 quorums intersect in at least one voter.

## Certification

- valid quorum-pair scenarios: 9
- scenarios with both valid certificates: 9
- branch-head collisions: 0
- same-tail tests: 9
- silent rejoins: 0
- minimum 2-of-3 quorum intersection: 1
- exact equivocation sets: 9
- equivocation-set errors: 0
- P1 branches surviving equivocation quarantine: 0
- P3 branches surviving equivocation quarantine: 0
- certificate voter-order tests: 18
- certificate order failures: 0
- different-head controls: 3
- different-head false equivocation: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
VALID CERT A
+
VALID CERT B
+
same parent
+
same pre-head
+
different children
::
CERTIFIED POLICY FORK
```

and, for this `2 / 3` parent geometry:

```text
quarantine equivocation intersection
↓
each branch loses at least one approval
↓
remaining approvals < 2
↓
neither child remains authorized
```

This is a safety halt, not a winner-selection rule.

```text
v39
!=
choose P1

v39
!=
choose P3

v39
=
preserve both branches
+
expose contradictory authority
+
halt canonical rotation
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
