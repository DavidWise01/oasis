# PAL-ZIP v96 — HIGHER-RECOVERY PREFIX FORK CONVERGENCE PROTECTION — FROZEN

**Parent:** PAL-ZIP v95  
**State:** FROZEN / 0e  
**Scope:** prove genuinely divergent v95 higher-recovery rank-chain prefixes remain distinct under identical future syntax.

## Target

v95 freezes:

```text
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-HEAD
::
depth
+
previous_prefix_head
+
exact v94 chain entry
```

v96 attacks silent convergence.

Three genuine divergent v95 depth-1 prefixes are created by separately quarantining:

```text
T0
T1
T2
```

Each seed is:

```text
rank_after = 2
status = ACTIVE
```

but each has a different clean-authority state.

Then every branch receives the exact same future tail entry at every later depth.

## Frozen recurrence

```text
P_(n+1)
:=
HIGHER-RECOVERY-PREFIX-MERGE-RECOVERY-RANK-PREFIX-HEAD(
  depth = n+1,
  previous_prefix_head = P_n,
  exact_future_entry = T_(n+1)
)
```

If:

```text
P_n(A) != P_n(B)
```

then under the same exact future entry:

```text
P_(n+1)(A) != P_(n+1)(B)
```

because the exact previous prefix remains part of identity.

## Stress depth

```text
64
```

identical future entries were appended to all three divergent seeds.

## Certification

- seed branches: 3
- seed prefix collisions: 0
- same-rank/different-state checks: 3
- same-rank/different-state failures: 0
- common-tail depth: 64
- pairwise divergence checks: 192
- false convergences: 0
- same-prefix determinism checks: 192
- determinism failures: 0
- global prefix heads checked: 195
- global prefix-head collisions: 0
- prefix-swap attacks: 192
- prefix swaps preserving head: 0
- future-entry tamper attacks: 192
- future-entry tamper preserving head: 0
- depth-tamper attacks: 192
- depth tamper preserving head: 0
- root-graft attacks: 192
- root graft preserving head: 0
- common-tail identity checks: 192
- common-tail identity failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
DIVERGED HIGHER-RECOVERY PREFIX
+
IDENTICAL FUTURE TAILS
::
STILL DIVERGED
```

Therefore:

```text
same future syntax
!=
same higher-recovery authority provenance
```

and:

```text
SAME RANK
!=
SAME HIGHER-RECOVERY AUTHORITY STATE
```

## Boundary

```text
v94 STATE CONTINUITY
::
separate validity gate
```

```text
v96
::
identity / provenance convergence protection
```

An explicit future convergence object is required to reunify genuinely divergent v95 histories.

No winner is selected.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
