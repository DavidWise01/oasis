# PAL-ZIP v36 — POLICY ROTATION FORK / UNIQUE DESCENDANT — FROZEN

**Parent:** PAL-ZIP v35  
**State:** FROZEN / 0e  
**Scope:** formal uniqueness of policy lineage.

## Sequential rotation semantics

A valid rotation transfers the active state:

```text
parent active
↓
POLICY-ROTATE(parent, child)
↓
child active
```

No extra `POLICY-ACTIVE(child)` marker is required for the transfer itself.

## Linear lineage

```text
P1
↓ rotate
P2
↓ rotate
P3
```

resolves to `P3`.

## Fork / stale-parent rules

```text
same active parent
├─ rotate → child A
└─ rotate → child B
::
UNRESOLVED
```

and:

```text
parent → child
then stale parent reactivated
::
UNRESOLVED
```

## Certification

- linear-chain controls: 1
- linear-chain failures: 0
- one-step controls: 3
- one-step failures: 0
- fork tests: 1
- false resolutions on fork: 0
- stale-parent reactivation tests: 2
- stale-parent false resolutions: 0
- wrong-parent rotation tests: 1
- wrong-parent false resolutions: 0
- unregistered-child tests: 1
- unregistered-child false resolutions: 0
- post-halt rotation tests: 1
- post-halt changes to resolution: 0
- distinct lineage-head tests: 3
- lineage-head collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
ONE LINEAR POLICY LINEAGE
::
ONE RESOLVED POLICY

POLICY FORK
::
NO RESOLUTION

STALE PARENT REACTIVATION
::
NO RESOLUTION
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
