# PAL-ZIP v34 — ACTIVE EXIT-POLICY UNIQUENESS — FROZEN

**Parent:** PAL-ZIP v33  
**State:** FROZEN / 0e  
**Scope:** formal anti-threshold-shopping policy selection.

## Target

v33 proves that policies themselves existed before the halt.

But multiple policies may have been registered.

v34 freezes the additional rule:

```text
exactly one policy
must be active
before the halt
```

Registration and activation are distinct:

```text
POLICY-REGISTER
!=
POLICY-ACTIVE
```

## Frozen resolution rule

```text
0 active policies
::
NO EXIT POLICY

1 active policy
::
RESOLVED

2+ distinct active policies
::
AMBIGUOUS
::
SAFE HALT CONTINUES
```

Repeated markers for the same active policy do not create another policy identity.

## Certification

- single-active controls: 3
- single-active failures: 0
- multiple-active ambiguity tests: 4
- false resolutions under ambiguity: 0
- zero-active tests: 1
- zero-active false resolutions: 0
- post-halt activation tests: 3
- post-halt false activations: 0
- registered-but-inactive tests: 3
- registered-but-inactive false resolutions: 0
- duplicate-same-policy tests: 3
- duplicate-same-policy failures: 0
- active-policy ancestry identity tests: 3
- active-policy ancestry collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
REGISTERED
::
available policy definition

ACTIVE
::
the one policy governing this halt
```

and:

```text
MULTIPLE DISTINCT ACTIVE POLICIES
::
NO THRESHOLD SHOPPING
::
SAFE HALT
```

So the kernel cannot choose `1/3`, `2/3`, or `3/3` opportunistically after the halt.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
