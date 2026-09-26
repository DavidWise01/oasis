# PAL-ZIP v60 — MERGE-RANK PREFIX FORK CONVERGENCE PROTECTION — FROZEN

**Parent:** PAL-ZIP v59  
**State:** FROZEN / 0e  
**Scope:** prove divergent merge-rank prefixes cannot silently converge under identical later tails.

## Target

v59 commits each merge-rank prefix head to its complete ordered ancestry.

v60 attacks the stronger identity case:

```text
prefix A != prefix B
```

followed by:

```text
same later tail token
same depth
same later append pattern
```

repeated many times.

The two prefix identities must remain distinct.

## Frozen recurrence

```text
P_(n+1)
:=
MERGE-RANK-PREFIX-HEAD(
  depth = n+1,
  previous_prefix = P_n,
  exact_tail = T_(n+1)
)
```

Therefore, if:

```text
P_n(A) != P_n(B)
```

then for the same exact tail and same exact depth:

```text
P_(n+1)(A) != P_(n+1)(B)
```

because the exact prior prefix is itself part of the committed identity.

## Seed geometry

Three genuine v59 depth-1 prefixes were built from the three valid first quarantines:

```text
remove T0
remove T1
remove T2
```

Each seed is therefore a valid descendant of the v57/v58/v59 lineage.

## Common-tail stress

Each divergent seed then received the same literal common-tail token at every later depth.

Stress depth:

```text
64
```

This is an identity-layer test.

v58 state continuity remains a separate validity gate. A literal common tail that is not valid
for both underlying merge-authority states does not become valid merely because v60 can encode it.

v60 proves the stronger identity property:

```text
even identical future syntax
cannot erase divergent provenance
```

## Certification

- seed branches: 3
- seed prefix collisions: 0
- common-tail depth: 64
- pairwise divergence checks: 192
- false convergences: 0
- same-prefix determinism checks: 192
- determinism failures: 0
- global prefix heads checked: 195
- global prefix-head collisions: 0
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
DIVERGED MERGE-RANK PREFIX
+
IDENTICAL FUTURE TAILS
::
STILL DIVERGED
```

So:

```text
same future syntax
!=
same merge-authority provenance
```

Only an explicit authorized convergence object may reunify divergent branches.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
