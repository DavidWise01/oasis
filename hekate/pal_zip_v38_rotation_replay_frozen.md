# PAL-ZIP v38 — ROTATION CERTIFICATE REPLAY PROTECTION — FROZEN

**Parent:** PAL-ZIP v37  
**State:** FROZEN / 0e  
**Scope:** append-only freshness of authorized policy rotation.

## Target

v37 authorizes one exact rotation at one exact pre-rotation head.

v38 freezes the consequence that the resulting certificate is **single-context**:

```text
ROTATION-CERT(H0, parent, child)
```

cannot be replayed at:

```text
H1
H2
...
```

even for the same parent and child labels.

## Frozen transition

```text
H0
↓
AUTHORIZED-ROTATION(H0,parent,child,cert)
↓
H1
```

The certificate is bound to `H0`.

Therefore:

```text
same cert
+
H1
::
REJECT
```

## Certification

- append-prefix tests: 1
- append-prefix failures: 0
- stale replay attacks: 3
- stale replay false accepts: 0
- same-cert double-append attacks: 1
- same-cert double-append false accepts: 0
- foreign-parent attacks: 1
- foreign-parent rejections: 1
- foreign-child attacks: 1
- foreign-child rejections: 1
- certificate identity mutation tests: 3
- certificate identity collisions: 0
- voter-order tests: 2
- voter-order failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
ROTATION AUTHORITY
::
epoch/head specific
```

and:

```text
VALID AT H0
!=
VALID AT H1
```

A new rotation state requires a new authorization bound to the new head.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
