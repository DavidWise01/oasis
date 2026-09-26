# PAL-ZIP v22 — RECOVERY AUTHORITY EQUIVOCATION — FROZEN

**Parent:** PAL-ZIP v21  
**State:** FROZEN / 0e  
**Scope:** formal contradiction detection in recovery authority.

## Target

v21 proves that different successor recoveries remain explicit fork branches.

v22 asks what it means if the same surviving old authority approves two different
`RECOVER` objects from the same recovery root.

## Frozen rule

```text
RECOVERY EQUIVOCATION
::
same survivor
+
same recovery_root
+
approve RECOVER_A
+
approve RECOVER_B
+
RECOVER_A != RECOVER_B
```

For the current recovery geometry, v19 requires unanimous approval from:

```text
G0
G3
```

Therefore if two different recoveries both obtain a valid 2/2 `RCERT`,
both survivors necessarily approved both conflicting recoveries.

## Certification

- distinct recovery branch pairs: 15
- double-authorized conflict scenarios: 15
- exact equivocation sets: 15
- equivocation-set errors: 0
- ordinary single-recovery controls: 6
- false equivocation on ordinary recovery: 0
- different-root controls: 6
- different-root false equivocation: 0
- effective old survivors after quarantining conflicting recovery approvers: 0
- conflicting recoveries retaining old-authority approval after quarantine: 0

**RESULT: 0e / PASS**

## Frozen consequence

```text
TWO VALID 2/2 RECOVERY CERTS
FOR DIFFERENT RECOVER OBJECTS
AT SAME RECOVERY ROOT
::
G0 equivocated
AND
G3 equivocated
```

Quarantining those recovery-equivocating authorities leaves:

```text
effective survivor authority
::
EMPTY
```

So neither conflicting recovery remains authorized by the old survivor set.

This is intentionally a safety halt.

```text
v22
::
exposes contradictory recovery authority

v22
!=
choose one successor

v22
!=
erase either branch
```

Both branches and both approval records remain evidence.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
