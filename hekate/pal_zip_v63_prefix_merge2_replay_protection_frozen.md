# PAL-ZIP v63 — PREFIX MERGE2 AUTHORIZATION REPLAY PROTECTION — FROZEN

**Parent:** PAL-ZIP v62  
**State:** FROZEN / 0e  
**Scope:** prevent v62 prefix-merge authority from surviving parent advance, epoch advance, or consumption.

## Target

v62 requires fresh authority from both exact prefix parents.

v63 freezes the lifecycle of that authorization.

A certificate valid for:

```text
(parent A, parent B, authority epoch E0)
```

must not remain valid after:

```text
A -> A'
B -> B'
E0 -> E1
```

or after the exact authorized merge object has already been consumed.

## Frozen consumption event

```text
PREFIX-MERGE-CONSUME
::
authority_epoch
+
exact AUTHORIZED-MERGE-RANK-PREFIX-MERGE2
```

The resulting consumed head is:

```text
PREFIX-MERGE-CONSUMED-HEAD
::
exact consume event
```

The next authority epoch is derived from that head:

```text
E1
:=
PREFIX-MERGE-AUTH-NEXT(consumed_head)
```

## Frozen replay rules

Old certificates are invalid after either exact parent advances:

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

Old certificates are also invalid in the next authority epoch:

```text
CERT(A,B,E0)
!=
CERT(A,B,E1)
```

And once the exact authorized object has been consumed:

```text
AUTHORIZE_ONCE(auth0, consumed={auth0})
::
REJECT
```

## Fresh continuation

The merge may be authorized again only with fresh certificates bound to the new epoch:

```text
fresh CERT(A,B,E1)
+
fresh CERT(B,A,E1)
::
new authorized object
```

The new authorized object is distinct from the consumed E0 authorization.

## Certification

- parent pairs: 3
- initial authorizations: 3
- initial authorization failures: 0
- parent-A advance attacks: 3
- false accepts: 0
- parent-B advance attacks: 3
- false accepts: 0
- epoch-advance attacks: 3
- false accepts: 0
- same-epoch post-consume replay attacks: 3
- false accepts: 0
- next-epoch old-cert replay attacks: 3
- false accepts: 0
- fresh next-epoch authorizations: 3
- fresh next-epoch failures: 0
- consumed-head / parent collisions: 0
- consumed-head / auth-object collisions: 0
- certificate order tests: 12
- certificate order failures: 0
- caller parent-order tests: 3
- caller parent-order failures: 0
- consumption determinism tests: 3
- consumption determinism failures: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID PREFIX-MERGE AUTHORITY
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
PARENT ADVANCE
```

```text
OLD CERTIFICATE
cannot survive
AUTHORITY-EPOCH ADVANCE
```

```text
CONSUMED AUTHORIZATION
cannot be replayed
inside the same consumed lineage
```

Fresh continuation requires fresh certificates.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
