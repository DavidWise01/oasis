# PAL-ZIP v33 — EXIT-POLICY ANCESTRY — FROZEN

**Parent:** PAL-ZIP v32  
**State:** FROZEN / 0e  
**Scope:** formal ancestry requirement for safe-halt exit policy.

## Target

v31/v32 bind votes and certificates to an explicit `EXIT-POLICY`.

v33 freezes the stronger rule:

```text
the exact policy must already exist
before
the SAFE-HALT event
in append-only ancestry
```

A threshold may not be invented after seeing the desired exit.

## Frozen registration

```text
POLICY-REGISTER
::
exact EXIT-POLICY
```

Required ordering:

```text
index(POLICY-REGISTER(policy))
<
index(SAFE-HALT)
```

## Certification

- pre-halt registration placements: 12
- pre-halt positive failures: 0
- post-halt registration placements: 9
- post-halt false accepts: 0
- missing-policy tests: 3
- missing-policy false accepts: 0
- wrong-policy tests: 6
- wrong-policy false accepts: 0
- before/after halt reorder tests: 3
- reorder false equivalences: 0
- policy-history identity tests: 3
- policy-history collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
POLICY CREATED AFTER HALT
::
NOT VALID FOR THAT HALT
```

and:

```text
1/3 policy ancestry
!=
2/3 policy ancestry
!=
3/3 policy ancestry
```

This prevents threshold-shopping after the failure state is already known.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
