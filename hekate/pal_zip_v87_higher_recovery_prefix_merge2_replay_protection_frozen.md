# PAL-ZIP v87 — HIGHER-RECOVERY PREFIX MERGE2 REPLAY PROTECTION — FROZEN

**Parent:** PAL-ZIP v86  
**State:** FROZEN / 0e  
**Scope:** invalidate v86 higher-recovery prefix merge authority after parent advance, epoch advance, or consumption.

## Target

v86 requires fresh dual-parent authority for the exact v85 structural convergence object.

v87 freezes that authorization lifecycle.

A certificate valid for:

```text
(parent A, parent B, authority epoch E0)
```

must not survive:

```text
A -> A'
B -> B'
E0 -> E1
```

or reuse after the exact authorized higher-recovery merge has been consumed.

## Frozen consume event

```text
HIGHER-RECOVERY-PREFIX-MERGE-CONSUME
::
authority_epoch
+
exact AUTHORIZED-HIGHER-RECOVERY-PREFIX-MERGE2
```

The resulting consumed head is:

```text
HIGHER-RECOVERY-PREFIX-MERGE-CONSUMED-HEAD
::
exact consume event
```

The next authority epoch derives from that exact consumed head:

```text
E1
:=
HIGHER-RECOVERY-PREFIX-MERGE-AUTH-NEXT(consumed_head)
```

## Frozen replay rules

Old certificates fail after exact parent advance:

```text
CERT(A,B,E0)
!=
CERT(A',B,E0)
```

```text
CERT(B,A,E0)
!=
CERT(B',A,E0)
```

Old certificates fail after authority-epoch advance:

```text
CERT(A,B,E0)
!=
CERT(A,B,E1)
```

Consumed authorization cannot replay:

```text
consume(auth0)
+
replay(auth0)
::
REJECT
```

## Fresh continuation

Fresh next-epoch authorization requires:

```text
fresh CERT(A,B,E1)
+
fresh CERT(B,A,E1)
::
new authorized higher-recovery merge
```

The new authorization is distinct from the consumed E0 authorization.

## Certification

- parent pairs: 3
- initial authorizations: 3
- initial authorization failures: 0
- parent-A advance attacks: 3
- parent-A false accepts: 0
- parent-B advance attacks: 3
- parent-B false accepts: 0
- epoch-advance attacks: 3
- epoch-advance false accepts: 0
- same-epoch post-consume replay attacks: 3
- same-epoch replay false accepts: 0
- next-epoch old-cert replay attacks: 3
- next-epoch old-cert false accepts: 0
- fresh next-epoch authorizations: 3
- fresh next-epoch failures: 0
- consumed-head / parent collisions: 0
- consumed-head / auth collisions: 0
- consumed-head pair collisions: 0
- certificate-order tests: 12
- certificate-order failures: 0
- caller parent-order tests: 3
- caller parent-order failures: 0
- consumption determinism tests: 3
- consumption determinism failures: 0
- next-epoch binding tests: 3
- next-epoch binding failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID HIGHER-RECOVERY PREFIX MERGE AUTHORITY
::
exact-parent specific
+
peer specific
+
epoch specific
+
single-consumption context
```

Therefore:

```text
OLD CERTIFICATE
cannot survive
HIGHER-RECOVERY PREFIX PARENT ADVANCE
```

```text
OLD CERTIFICATE
cannot survive
AUTHORITY-EPOCH ADVANCE
```

```text
CONSUMED AUTHORIZATION
cannot replay
inside the same consumed lineage
```

Fresh continuation requires fresh certificates.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
