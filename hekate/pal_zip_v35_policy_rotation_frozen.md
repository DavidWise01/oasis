# PAL-ZIP v35 — EXIT-POLICY ROTATION LINEAGE — FROZEN

**Parent:** PAL-ZIP v34  
**State:** FROZEN / 0e  
**Scope:** formal ancestry for changing the active exit policy before a future halt.

## Target

Allow an exit policy to change **before a future halt**, but require explicit ancestry.

A child policy cannot simply appear.

## Frozen rotation

```text
POLICY-ROTATE
::
parent_policy
+
child_policy
```

A valid rotation requires the ordered witness:

```text
POLICY-REGISTER(parent)
↓
POLICY-ACTIVE(parent)
↓
POLICY-REGISTER(child)
↓
POLICY-ROTATE(parent, child)
↓
SAFE-HALT
```

## Invalid forms

```text
missing parent registration
missing parent active state
missing child registration
wrong parent
rotation after halt
self rotation
```

all fail.

## Certification

- valid rotation controls: 3
- valid rotation failures: 0
- missing-parent-register tests: 3
- false accepts: 0
- missing-parent-active tests: 3
- false accepts: 0
- missing-child-register tests: 3
- false accepts: 0
- wrong-parent tests: 3
- false accepts: 0
- post-halt rotation tests: 3
- post-halt false accepts: 0
- self-rotation tests: 3
- self-rotation rejections: 3
- rotation-history identity tests: 3
- history collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
POLICY CHANGE
::
must descend from
the currently active parent policy
```

So:

```text
2/3 → 3/3
```

or:

```text
3/3 → 1/3
```

cannot appear without an explicit parent-child rotation record in ancestry.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
