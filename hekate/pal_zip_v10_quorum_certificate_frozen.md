# PAL-ZIP v10 — QUORUM CERTIFICATE BIND — FROZEN

**Parent:** PAL-ZIP v09  
**State:** FROZEN / 0e  
**Scope:** formal quorum-certificate identity.

## Target

v09 determines whether a merge has enough authority.

v10 makes the authority result itself one bound object:

```text
QCERT
::
MERGE2 identity
+
canonical voter/decision set
```

So a certificate cannot be moved from one merge to another.

## Certification

- order-permutation tests: 6
- order-permutation failures: 0
- merge-swap attacks: 2
- merge-swap false accepts: 0
- voter-set swap attacks: 3
- voter-set false accepts: 0
- decision-flip attacks: 3
- decision-flip false accepts: 0

**RESULT: 0e / PASS**

## Frozen invariants

```text
same voters
+
same merge
+
different input order
::
same QCERT
```

but:

```text
different merge
::
different QCERT

different voter set
::
different QCERT

decision flip below threshold
::
no valid QCERT
```

## Current authority chain

```text
MERGE2
↓
3-of-4 approval
↓
QCERT
↓
append-only descendant
```

The next target is to bind `QCERT` into the v06/v07 append-only history so authorization itself becomes part of the permanent provenance path.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
