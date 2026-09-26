# PAL-ZIP v20 — SUCCESSOR ACTIVATION / NO RETROACTIVE AUTHORITY — FROZEN

**Parent:** PAL-ZIP v19  
**State:** FROZEN / 0e  
**Scope:** formal activation boundary for the recovered committee.

## Target

A successor committee must begin at a specific activation point.

Old votes cannot be carried forward.
New-member votes cast before activation cannot be carried backward or forward into the activated state.

## Frozen activation

```text
ACTIVATE
::
prior_head
+
exact RECOVER object
+
exact RCERT
+
successor committee
```

The activation is appended:

```text
prior head
↓
ACTIVATE
↓
activation head
```

Normal 3-of-4 voting for the successor committee begins only on that activation head.

## Certification

- valid new 3-of-4 controls: 4
- valid-control failures: 0
- old-vote replay attacks: 4
- old-vote replay false accepts: 0
- pre-activation newcomer attacks: 2
- pre-activation newcomer false accepts: 0
- mixed old/new splice attacks: 4
- mixed old/new false accepts: 0
- foreign recovery-cert attacks: 1
- foreign recovery-cert rejections: 1
- activation-context mutations: 3
- activation mutations preserving same event: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
OLD AUTHORITY
::
ends at recovery/activation boundary

NEW AUTHORITY
::
begins at activation head
```

Therefore:

```text
IDENTITY CONTINUITY
!=
VOTE CONTINUITY
```

A voter identity that exists on both committees still needs a fresh vote in the fresh context.

## Recovery chain

```text
QUARANTINE
↓
RECOVER
↓
RCERT
↓
ACTIVATE
↓
NEW COMMITTEE 3/4
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
