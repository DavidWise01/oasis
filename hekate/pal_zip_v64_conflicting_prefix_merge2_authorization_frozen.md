# PAL-ZIP v64 — CONFLICTING PREFIX-MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v63  
**State:** FROZEN / 0e  
**Scope:** same exact prefix parent + same authority epoch authorizing two different peer-prefix merges.

## Target

v63 freezes replay protection and single-consumption context.

v64 attacks a pre-consumption conflict:

```text
same exact prefix parent A
+
same authority epoch E0
+
authorize MERGE2(A,B)
+
authorize MERGE2(A,C)
```

Both merges may individually satisfy v62/v63 authorization.

That creates a certified prefix-merge fork, not two canonical convergences.

## Frozen prefix-merge equivocation

```text
same voter
+
same exact parent prefix
+
same authority epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
PREFIX-MERGE EQUIVOCATION
```

## Certified fork

```text
PREFIX A ---- MERGE2(A,B) ----> branch AB
    \
     \--- MERGE2(A,C) ----> branch AC
```

The two authorized branch heads remain distinct.

Appending the same later tail does not erase the fork.

## Quarantine consequence

For the frozen `2 / 3` authority geometry, two valid shared-parent quorums always overlap.

The exact overlap is the equivocation set.

Append:

```text
PREFIX-MERGE-QUARANTINE
::
exact parent prefix
+
exact authority epoch
+
exact equivocator set
+
both conflicting authorized-merge references
```

After removing the equivocator set from the shared parent authority:

```text
AB support < 2
AC support < 2
```

so neither conflicting convergence remains authorized through parent A.

## Certification

- shared-parent quorum-pair scenarios: 9
- both prefix merges individually authorized: 9
- branch-head collisions: 0
- same-tail tests: 9
- silent rejoins: 0
- minimum quorum intersection: 1
- exact equivocator sets: 9
- equivocator-set errors: 0
- quarantine events: 9
- AB surviving quarantine: 0
- AC surviving quarantine: 0
- certificate ordering tests: 18
- ordering failures: 0
- different-epoch controls: 3
- different-epoch false equivocation: 0
- same-merge repeat controls: 3
- same-merge repeat false equivocation: 0
- different-parent controls: 3
- different-parent false equivocation: 0
- quarantine context-tamper attacks: 18
- context tamper preserving same event: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID PREFIX MERGE AUTH A-B
+
VALID PREFIX MERGE AUTH A-C
+
same exact parent A
+
same authority epoch
::
CERTIFIED PREFIX-MERGE FORK
```

and:

```text
shared-parent equivocation
::
quarantine exact overlap
::
neither conflicting merge remains authorized
```

No winner is selected.

No conflicting authorization is consumed as canonical while the fork is unresolved.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
