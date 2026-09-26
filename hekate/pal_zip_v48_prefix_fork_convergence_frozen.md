# PAL-ZIP v48 — PREFIX FORK CONVERGENCE PROTECTION — FROZEN

**Parent:** PAL-ZIP v47  
**State:** FROZEN / 0e  
**Scope:** prove divergent valid prefixes cannot silently converge by receiving identical later tails.

## Target

v47 commits every head to its complete ordered prefix.

v48 attacks the stronger case:

```text
branch A prefix != branch B prefix
```

followed by:

```text
same witness tail
same depth
same later append pattern
```

repeated many times.

The branches must remain distinct forever unless an explicit merge primitive is introduced.

## Frozen recurrence

```text
H_(n+1)
:=
PREFIX-HEAD(
  depth = n+1,
  previous = H_n,
  witness = W_(n+1)
)
```

If:

```text
H_n(A) != H_n(B)
```

then for the same exact witness `W_(n+1)` and the same exact depth:

```text
H_(n+1)(A) != H_(n+1)(B)
```

because the previous prefix head is itself part of the committed identity.

## Frozen test geometry

Three valid v47 seed branches were used:

```text
remove T0
remove T1
remove T2
```

Each branch then received the **same literal common-tail witness** at every later depth.

Common tail depth exercised:

```text
64
```

## Certification

- seed branches: 3
- seed-head collisions: 0
- common-tail depth: 64
- pairwise divergence checks: 192
- false convergences: 0
- same-prefix determinism checks: 192
- determinism failures: 0
- global heads checked: 195
- global head collisions: 0
- prefix-swap attacks: 192
- prefix swaps reproducing original head: 0
- tail-tamper attacks: 192
- tail tamper preserving head: 0
- depth-tamper attacks: 192
- depth tamper preserving head: 0
- common-tail identity checks: 192
- common-tail identity failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
DIVERGED PREFIX
+
IDENTICAL FUTURE TAILS
::
STILL DIVERGED
```

So:

```text
A -- W2 -- W3 -- ... -- W65
B -- W2 -- W3 -- ... -- W65
```

cannot silently become:

```text
same canonical head
```

when `A != B`.

## Boundary

v48 does **not** forbid an explicit authorized merge object.

It forbids **implicit convergence** caused merely by appending identical later witnesses.

```text
same future
!=
same provenance
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
