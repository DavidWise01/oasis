# PAL-ZIP v25 — RESERVE EQUIVOCATION / CAPTURE PROTECTION — FROZEN

**Parent:** PAL-ZIP v24  
**State:** FROZEN / 0e  
**Scope:** formal contradiction detection in emergency reserve authority.

## Target

v23 introduced a pre-anchored reserve:

```text
R0 R1 R2 R3
threshold :: 3 / 4
```

v25 tests the failure case where the reserve itself approves two different
`VACUUM-RECOVER` objects from the same vacuum root.

## Frozen rule

```text
RESERVE EQUIVOCATION
::
same reserve voter
+
same vacuum_root
+
approve RECOVER_A
+
approve RECOVER_B
+
RECOVER_A != RECOVER_B
```

## Quorum geometry

For four reserve voters with threshold three:

```text
any 3/4 quorum
intersects any other 3/4 quorum
in at least 2 voters
```

Therefore two conflicting 3-of-4 reserve certificates cannot coexist
without reserve equivocation.

## Exhaustive certification

- recovery objects: 5
- reserve 3-of-4 quorums: 4
- conflicting recovery pairs: 10
- quorum-pair conflict scenarios: 160
- minimum quorum intersection: 2
- exact equivocation sets: 160
- equivocation-set errors: 0
- RECOVER_A surviving quarantine: 0
- RECOVER_B surviving quarantine: 0
- ordinary single-recovery controls: 20
- ordinary false equivocation: 0
- different-root controls: 12
- different-root false equivocation: 0
- full reserve-capture attacks: 10
- full-capture exact detections: 10

**RESULT: 0e / PASS**

## Frozen consequence

```text
CONFLICTING RESERVE 3/4 + 3/4
::
equivocation intersection >= 2
```

Quarantine those equivocal reserve votes for that exact vacuum root:

```text
remaining usable reserve authority
<= 2
```

which is below the 3-of-4 threshold.

Therefore neither conflicting recovery remains authorized.

## Capture case

If all four reserve identities approve both conflicting recoveries:

```text
quarantine set
::
R0 R1 R2 R3

effective reserve authority
::
EMPTY
```

v25 exposes the capture; it does not select a successor or erase either recovery branch.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
