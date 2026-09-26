# PAL-ZIP v29 — MULTI-PREANCHOR EXIT FORK / EQUIVOCATION — FROZEN

**Parent:** PAL-ZIP v28  
**State:** FROZEN / 0e  
**Scope:** formal safe-halt exit fork detection.

## Target

v28 allows a safe-halt exit only through authority registered before the halt.

v29 handles the case where more than one legitimate pre-anchored authority exists:

```text
T0 :: pre-anchored
T1 :: pre-anchored
```

and they authorize incompatible exits from the same halt head.

## Frozen exit intent

```text
SAFE-HALT-EXIT
::
halt_head
+
source
+
action
+
target
```

## Conflict rule

```text
same halt_head
+
different (action,target)
::
EXIT FORK
```

while:

```text
same halt_head
+
same (action,target)
+
different pre-anchored sources
::
corroboration
NOT conflict
```

Source identity still remains part of provenance.

## Certification

- same-intent controls: 12
- false conflicts on same intent: 0
- conflicting exit pairs: 66
- conflicts detected: 66
- conflicts missed: 0
- different-head controls: 4
- different-head false conflicts: 0
- branch pairs checked: 66
- equal branch-head failures: 0
- same-tail tests: 66
- silent rejoins: 0
- explicit MERGE2 tests: 66
- merge-order failures: 0
- source-identity tests: 12
- source-identity collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
PRE-ANCHORED
!=
UNILATERAL RIGHT TO COLLAPSE CONFLICT
```

Two contradictory legitimate exits remain two explicit branch histories:

```text
SAFE-HALT
   |
   +---- T0 -> EXIT_A
   |
   +---- T1 -> EXIT_B
```

Appending the same later payload does not erase the fork.

An explicit parent-preserving `MERGE2` can join the branch histories, but v29 does not
decide which exit should become operating authority.

## Safety boundary

```text
v29
::
detects and preserves exit contradiction

v29
!=
choose T0

v29
!=
choose T1

v29
!=
silently activate both
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
