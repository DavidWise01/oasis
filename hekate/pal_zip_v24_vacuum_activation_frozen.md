# PAL-ZIP v24 — VACUUM SUCCESSOR ACTIVATION — FROZEN

**Parent:** PAL-ZIP v23  
**State:** FROZEN / 0e  
**Scope:** formal activation boundary after authority-vacuum recovery.

## Target

A v23 successor committee does not become active merely because the reserve approved
its creation.

Authority begins only at an explicit activation head.

## Frozen activation

```text
VACUUM-ACTIVATE
::
vacuum_root
+
exact VACUUM-RECOVER
+
exact VRCERT
+
successor committee
```

Then:

```text
vacuum root
↓
VACUUM-ACTIVATE
↓
activation head
↓
fresh successor 3 / 4 voting
```

## No authority carry-over

Votes from these sources do not count in the successor committee:

```text
reserve authority
implicated prior authority
pre-activation successor votes
```

Every successor vote must be fresh and bound to the activation head.

## Certification

- valid fresh successor quorums: 4
- valid-control failures: 0
- reserve-vote replay attacks: 4
- reserve-vote replay false accepts: 0
- implicated-vote replay attacks: 4
- implicated-vote replay false accepts: 0
- pre-activation successor attacks: 4
- pre-activation successor false accepts: 0
- foreign VRCERT attacks: 1
- foreign VRCERT rejections: 1
- activation-context mutations: 3
- activation mutations preserving same event: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
RESERVE AUTHORITY
::
authorizes recovery

SUCCESSOR AUTHORITY
::
begins only at activation head
```

So:

```text
RECOVERY AUTHORITY
!=
OPERATING AUTHORITY
```

and:

```text
IDENTITY CONTINUITY
!=
VOTE CONTINUITY
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
