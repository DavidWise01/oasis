# PAL-ZIP v76 — CONFLICTING RECOVERY-RANK PREFIX MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v75  
**State:** FROZEN / 0e  
**Scope:** same exact recovery-prefix parent + same authority epoch authorizing two different peer recovery-prefix merges.

## Target

v75 freezes replay protection and single-consumption context.

v76 attacks a pre-consumption conflict:

```text
same exact recovery-prefix parent A
+
same authority epoch E0
+
authorize MERGE2(A,B)
+
authorize MERGE2(A,C)
```

Both merges can independently satisfy v74/v75 authorization.

That creates a certified recovery-prefix merge fork, not two canonical convergences.

## Frozen equivocation

```text
same voter
+
same exact recovery-prefix parent
+
same authority epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
RECOVERY-RANK PREFIX-MERGE EQUIVOCATION
```

## Certified fork

```text
RECOVERY PREFIX A ---- MERGE2(A,B) ----> branch AB
          \
           \--- MERGE2(A,C) ----> branch AC
```

The authorized branch heads remain distinct.

Appending the same later tail does not erase the fork.

## Quarantine consequence

Under the frozen `2 / 3` authority geometry, two valid shared-parent quorums always overlap.

The exact overlap is the equivocation set.

Append:

```text
RECOVERY-RANK-PREFIX-MERGE-QUARANTINE
::
exact recovery-prefix parent
+
exact authority epoch
+
exact equivocator set
+
both conflicting authorized-merge references
```

After removing the equivocation set from the shared-parent authority:

```text
AB support < 2
AC support < 2
```

so neither conflicting convergence remains authorized through parent A.

## Certification

- shared-parent quorum-pair scenarios: 9
- both merges individually authorized: 9
- branch-head collisions: 0
- same-tail tests: 9
- silent rejoins: 0
- minimum quorum intersection: 1
- exact equivocator sets: 9
- equivocator-set errors: 0
- quarantine events: 9
- AB surviving quarantine: 0
- AC surviving quarantine: 0
- certificate-order tests: 18
- certificate-order failures: 0
- different-epoch controls: 3
- different-epoch false equivocation: 0
- same-merge repeat controls: 3
- same-merge repeat false equivocation: 0
- different-parent controls: 3
- different-parent false equivocation: 0
- quarantine-context tamper attacks: 18
- context-tamper same-event results: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID RECOVERY-PREFIX MERGE AUTH A-B
+
VALID RECOVERY-PREFIX MERGE AUTH A-C
+
same exact parent A
+
same authority epoch
::
CERTIFIED RECOVERY-PREFIX MERGE FORK
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
