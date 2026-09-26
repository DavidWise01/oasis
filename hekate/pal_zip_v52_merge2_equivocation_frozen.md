# PAL-ZIP v52 — CONFLICTING MERGE2 AUTHORIZATION / MERGE EQUIVOCATION — FROZEN

**Parent:** PAL-ZIP v51  
**State:** FROZEN / 0e  
**Scope:** same parent + same epoch authorizing two different peer merges.

## Target

v51 binds merge certificates to exact parent/peer/epoch context.

v52 attacks the case:

```text
same parent A
+
same merge epoch E0
+
A approves MERGE2(A,B)
+
A approves MERGE2(A,C)
```

Both merges may individually satisfy v50/v51 authorization.

That does **not** make both convergence paths canonical.

## Frozen merge-equivocation rule

```text
same voter
+
same parent
+
same epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
MERGE EQUIVOCATION
```

For the frozen parent policy:

```text
members
::
T0 T1 T2

threshold
::
2 / 3
```

two valid 2-of-3 quorums from the same parent always intersect in at least one voter.

## Certified merge fork

```text
A ---- MERGE2(A,B) ----> branch AB
 \
  \--- MERGE2(A,C) ----> branch AC
```

Both branch objects remain distinct.

Appending the same later tail does not erase the fork.

## Quarantine consequence

The exact shared-parent quorum intersection is the equivocator set.

After quarantining that intersection:

```text
AB approvals < 2
AC approvals < 2
```

so neither conflicting merge remains authorized through parent A.

Peer-side certificates for B and C remain preserved as evidence.

## Certification

- parent-A quorum-pair scenarios: 9
- scenarios with both merges individually authorized: 9
- merge-branch collisions: 0
- same-tail tests: 9
- silent rejoins: 0
- minimum shared-parent quorum intersection: 1
- exact equivocation sets: 9
- equivocation-set errors: 0
- AB branches surviving quarantine: 0
- AC branches surviving quarantine: 0
- certificate order tests: 18
- certificate order failures: 0
- different-epoch controls: 3
- different-epoch false equivocation: 0
- same-merge repeat controls: 3
- same-merge repeat false equivocation: 0
- different-parent controls: 3
- different-parent false equivocation: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID MERGE AUTH A-B
+
VALID MERGE AUTH A-C
+
same parent A
+
same epoch
::
CERTIFIED MERGE FORK
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

```text
v52
!=
prefer B

v52
!=
prefer C

v52
=
preserve both merge branches
+
expose shared-parent contradictory authority
+
halt canonical convergence
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
