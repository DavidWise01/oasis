# PAL-ZIP v75 — RECOVERY-RANK PREFIX MERGE2 REPLAY PROTECTION — FROZEN

**Parent:** PAL-ZIP v74  
**State:** FROZEN / 0e  
**Scope:** invalidate v74 recovery-prefix merge authority after parent advance, epoch advance, or consumption.

## Target

v74 requires fresh authority from both exact recovery-prefix parents.

v75 freezes the lifecycle of that authorization.

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

or reuse after the exact authorized merge has been consumed.

## Frozen consume event

```text
RECOVERY-RANK-PREFIX-MERGE-CONSUME
::
authority_epoch
+
exact AUTHORIZED-RECOVERY-RANK-PREFIX-MERGE2
```

The resulting head is:

```text
RECOVERY-RANK-PREFIX-MERGE-CONSUMED-HEAD
::
exact consume event
```

The next authority epoch is derived from that exact consumed head:

```text
E1
:=
RECOVERY-RANK-PREFIX-MERGE-AUTH-NEXT(consumed_head)
```

## Frozen replay rules

Old certificates are invalid after either exact recovery-prefix parent advances:

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

Old certificates are invalid in the next authority epoch:

```text
CERT(A,B,E0)
!=
CERT(A,B,E1)
```

Once the exact authorized merge has been consumed:

```text
AUTHORIZE_ONCE(auth0, consumed={auth0})
::
REJECT
```

## Fresh continuation

A new authorization requires fresh certificates bound to the exact next epoch:

```text
fresh CERT(A,B,E1)
+
fresh CERT(B,A,E1)
::
new authorized object
```

That new authorization is distinct from the consumed E0 authorization.

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
VALID RECOVERY-PREFIX MERGE AUTHORITY
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
RECOVERY-PREFIX PARENT ADVANCE
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
