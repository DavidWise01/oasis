# PAL-ZIP v100 — CONFLICTING HIGHER-RECOVERY RANK-PREFIX MERGE2 AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v99  
**State:** FROZEN / 0e  
**Scope:** same exact higher-recovery rank-prefix parent + same authority epoch authorizing two different exact v99 peer merges.

## Target

v99 freezes exact-parent, peer, merge, epoch, and single-consumption replay protection.

v100 attacks a pre-consumption conflict:

```text
same exact higher-recovery rank-prefix parent A
+
same authority epoch E0
+
authorize MERGE2(A,B)
+
authorize MERGE2(A,C)
```

Both merges may independently satisfy v98/v99 authorization.

That creates a certified higher-recovery rank-prefix merge fork.

It does not select a canonical convergence.

## Frozen equivocation

```text
same voter
+
same exact higher-recovery rank-prefix parent
+
same authority epoch
+
approve peer B / merge AB
+
approve peer C / merge AC
+
AB != AC
::
HIGHER-RECOVERY RANK-PREFIX MERGE EQUIVOCATION
```

## Certified fork

```text
HIGHER-RECOVERY RANK-PREFIX A ---- MERGE2(A,B) ----> branch AB
                    \
                     \--- MERGE2(A,C) ----> branch AC
```

The authorized branch heads remain distinct.

Appending identical future syntax does not silently reunify them.

## Quarantine consequence

Under the frozen `2 / 3` authority, two valid shared-parent quorums always overlap.

That exact intersection is the equivocation set.

Append:

```text
HIGHER-RECOVERY-RANK-PREFIX-MERGE-QUARANTINE
::
exact rank-prefix parent
+
exact authority epoch
+
exact equivocator set
+
both conflicting authorized-merge references
```

After removing that exact overlap:

```text
AB support < 2
AC support < 2
```

so neither conflicting rank-prefix convergence remains authorized through parent A.

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
- authorized-reference tamper attacks: 18
- authorized-reference tamper same-event results: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID HIGHER-RECOVERY RANK-PREFIX MERGE AUTH A-B
+
VALID HIGHER-RECOVERY RANK-PREFIX MERGE AUTH A-C
+
same exact parent A
+
same authority epoch
::
CERTIFIED HIGHER-RECOVERY RANK-PREFIX MERGE FORK
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

No conflicting authorization is silently consumed as canonical while the fork is unresolved.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
