# PAL-ZIP v51 — MERGE2 CERTIFICATE REPLAY PROTECTION — FROZEN

**Parent:** PAL-ZIP v50  
**State:** FROZEN / 0e  
**Scope:** prevent dual-parent merge authorization from being replayed after either parent or the merge epoch changes.

## Target

v50 requires two parent-bound certificates for:

```text
MERGE2(A,B)
```

v51 freezes those certificates to the exact:

```text
parent A head
parent B head
merge object
merge epoch/head
```

## Frozen parent certificate

```text
PARENT-MERGE-CERT
::
parent_head
+
peer_head
+
exact MERGE2(parent,peer)
+
epoch_head
+
threshold
+
canonical approvals
```

The peer head is explicit, so a certificate for:

```text
A with B
```

cannot be reused for:

```text
A with C
```

## Replay rule

If either parent advances:

```text
A -> A'
```

or:

```text
B -> B'
```

then the old certificates are stale.

Likewise, after the merge epoch advances:

```text
E0
↓ authorized MERGE2
E1
```

certificates bound to `E0` do not authorize another merge at `E1`.

## Certification

- parent pairs: 3
- valid authorizations: 3
- valid authorization failures: 0
- parent-A advance attacks: 3
- parent-A advance false accepts: 0
- parent-B advance attacks: 3
- parent-B advance false accepts: 0
- epoch-advance attacks: 3
- epoch-advance false accepts: 0
- post-merge replay attacks: 3
- post-merge replay false accepts: 0
- foreign-peer attacks: 3
- foreign-peer false accepts: 0
- certificate-order tests: 12
- certificate-order failures: 0
- caller-parent-order tests: 3
- caller-parent-order failures: 0
- merged-head / parent collisions: 0
- merged-head / epoch collisions: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID AT (A,B,E0)
!=
VALID AT (A',B,E0)
!=
VALID AT (A,B',E0)
!=
VALID AT (A,B,E1)
```

Therefore:

```text
MERGE AUTHORITY
::
exact-parent specific
+
peer specific
+
epoch specific
```

A successful merge consumes that authorization context.

A later merge requires fresh certificates bound to the new exact state.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
