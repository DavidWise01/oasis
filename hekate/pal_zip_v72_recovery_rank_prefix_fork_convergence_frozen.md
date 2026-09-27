# PAL-ZIP v72 — RECOVERY-RANK PREFIX FORK CONVERGENCE PROTECTION — FROZEN

**Parent:** PAL-ZIP v71  
**State:** FROZEN / 0e  
**Scope:** prove divergent v71 recovery-rank prefixes cannot silently converge under identical later tails.

## Target

v71 commits every recovery-rank prefix head to the entire ordered v70 ancestry.

v72 attacks the stronger convergence case:

```text
prefix A != prefix B
```

followed by identical later syntax:

```text
same depth
+
same later tail token
+
same append pattern
```

repeated across many rounds.

The two recovery-prefix identities must remain distinct.

## Frozen recurrence

```text
P_(n+1)
:=
PREFIX-MERGE-RECOVERY-RANK-PREFIX-HEAD(
  depth = n+1,
  previous_prefix = P_n,
  exact_tail = T_(n+1)
)
```

Therefore:

```text
P_n(A) != P_n(B)
```

with the same exact tail `T_(n+1)` implies:

```text
P_(n+1)(A) != P_(n+1)(B)
```

because the exact previous v71 prefix is part of the committed identity.

## Seed geometry

Three genuine divergent v71 seed prefixes were built by quarantining exactly one distinct authority identity:

```text
remove T0
remove T1
remove T2
```

Each leaves rank `2`, but each leaves a different eligible authority state.

So:

```text
SAME RANK
!=
SAME AUTHORITY STATE
```

is preserved before the convergence stress begins.

## Common-tail stress

Each divergent seed then received the exact same literal future tail token at every later depth.

Stress depth:

```text
64
```

This is an identity/provenance test.

The v70/v71 state-continuity gates remain separate validity checks.

v72 proves:

```text
even identical future syntax
cannot erase divergent recovery provenance
```

## Certification

- seed branches: 3
- seed prefix collisions: 0
- same-rank/different-state checks: 3
- same-rank/different-state failures: 0
- common-tail depth: 64
- pairwise divergence checks: 192
- false convergences: 0
- global prefix heads checked: 195
- global prefix-head collisions: 0
- prefix-swap attacks: 192
- prefix swaps reproducing original head: 0
- tail-tamper attacks: 192
- tail tamper preserving head: 0
- depth-tamper attacks: 192
- depth tamper preserving head: 0
- same-prefix determinism checks: 192
- determinism failures: 0
- common-tail identity checks: 192
- common-tail identity failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
DIVERGED RECOVERY-RANK PREFIX
+
IDENTICAL FUTURE TAILS
::
STILL DIVERGED
```

Therefore:

```text
same future syntax
!=
same recovery provenance
```

Only an explicit future convergence object may reunify divergent v71 recovery histories.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
