# PAL-ZIP v30 — SAFE-HALT EXIT CONFLICT GATE — FROZEN

**Parent:** PAL-ZIP v29  
**State:** FROZEN / 0e  
**Scope:** formal safety gate for contradictory pre-anchored exits.

## Target

v29 detects multiple legitimate pre-anchored exit branches.

v30 freezes the immediate safety consequence:

```text
EXIT CONFLICT
::
remain halted
```

## Frozen gate

```text
same halt_head
+
more than one distinct (action,target)
::
BLOCK
```

while:

```text
same halt_head
+
one shared (action,target)
::
NO CONFLICT BLOCK
```

Important:

```text
NO CONFLICT BLOCK
!=
AUTHORIZED EXIT
```

v30 is only a conflict gate. It does not invent a quorum, winner, priority, or authority policy.

## Certification

- conflicting sets tested: 66
- conflicting sets blocked: 66
- conflicting sets not blocked: 0
- same-intent corroboration sets: 12
- false blocks on same intent: 0
- single-source controls: 12
- false blocks on single source: 0
- different-head controls: 6
- false blocks across different heads: 0
- auto-advance checks: 96
- unauthorized auto-advances: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
CONTRADICTORY PRE-ANCHORED EXITS
::
EXPLICIT FORK
+
SAFE HALT CONTINUES
```

and:

```text
CORROBORATION
::
removes this particular conflict condition

but

CORROBORATION
!=
authorization by itself
```

This preserves the separation between:

```text
CONSISTENCY
and
AUTHORITY
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
