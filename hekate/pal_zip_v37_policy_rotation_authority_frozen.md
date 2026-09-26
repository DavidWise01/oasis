# PAL-ZIP v37 — POLICY-ROTATION AUTHORIZATION — FROZEN

**Parent:** PAL-ZIP v36  
**State:** FROZEN / 0e  
**Scope:** authority for changing the active policy lineage.

## Target

v35/v36 define the geometry of a valid policy rotation.

v37 adds the missing authority rule:

```text
POLICY-ROTATE(parent, child)
```

cannot enter the authorized lineage merely because someone wrote it.

## Frozen authority source

The **current parent policy** authorizes its own replacement.

```text
rotation authority
::
parent policy members
+
parent policy threshold
```

The child policy does not authorize its own installation.

Therefore:

```text
parent 3/3 -> child 1/3
```

still requires:

```text
3 / 3
```

for the rotation itself.

## Frozen rotation vote

```text
ROTATION-VOTE
::
voter
+
pre_rotation_head
+
parent_policy
+
child_policy
+
decision
```

## Frozen certificate

```text
ROTATION-CERT
::
pre_rotation_head
+
exact parent
+
exact child
+
canonical parent-policy vote set
```

and:

```text
AUTHORIZED-ROTATION
::
exact POLICY-ROTATE
+
exact ROTATION-CERT
```

## Certification

- rotation pairs: 3
- parent-policy approval subsets: 24
- subset mismatches: 0
- child-threshold self-install attacks: 1
- child-threshold false accepts: 0
- duplicate attacks: 2
- duplicate false accepts: 0
- outsider attacks: 2
- outsider false accepts: 0
- wrong-head attacks: 2
- wrong-head false accepts: 0
- wrong-parent attacks: 2
- wrong-parent false accepts: 0
- wrong-child attacks: 2
- wrong-child false accepts: 0
- certificate order tests: 9
- certificate order failures: 0
- foreign-certificate attacks: 3
- foreign-certificate rejections: 3

**RESULT: 0e / PASS**

## Frozen invariant

```text
CHILD POLICY
::
cannot lower the authority needed
to install itself
```

and:

```text
ROTATION AUTHORITY
::
bound to
parent + child + pre-rotation head
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
