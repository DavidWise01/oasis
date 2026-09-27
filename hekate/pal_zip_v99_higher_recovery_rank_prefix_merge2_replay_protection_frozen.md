# PAL-ZIP v99 — HIGHER-RECOVERY RANK-PREFIX MERGE2 REPLAY PROTECTION — FROZEN

**Parent:** PAL-ZIP v98  
**State:** FROZEN / 0e  
**Scope:** bind higher-recovery rank-prefix merge authorization to exact parents, peer, epoch, and single-consumption context.

## Target

v98 proves dual-parent authorization for the exact v97 structural convergence object.

v99 freezes the authorization lifecycle.

A valid v98 certificate is specific to:

```text
exact parent
+
exact peer
+
exact MERGE2(parent,peer)
+
exact authority epoch
```

and an exact authorized merge may be consumed only once in its lineage.

## Frozen consumption

```text
HIGHER-RECOVERY-RANK-PREFIX-MERGE-CONSUME
::
authority_epoch
+
exact AUTHORIZED-HIGHER-RECOVERY-RANK-PREFIX-MERGE2
```

The consumed head is:

```text
HIGHER-RECOVERY-RANK-PREFIX-MERGE-CONSUMED-HEAD
::
exact consume event
```

The next authority epoch derives from that exact consumed head:

```text
E1
:=
HIGHER-RECOVERY-RANK-PREFIX-MERGE-AUTH-NEXT(consumed_head)
```

## Replay rules

Old certificates fail after exact-parent advance:

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

Old certificates fail under peer substitution:

```text
CERT(A,B,E0)
!=
CERT(A,C,E0)
```

Old certificates fail after epoch advance:

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

Fresh next-epoch certificates are required:

```text
fresh CERT(A,B,E1)
+
fresh CERT(B,A,E1)
::
new authorized higher-recovery rank-prefix merge
```

The new authorization is distinct from consumed `auth0`.

## Certification

- parent pairs: 3
- initial authorizations: 3
- initial authorization failures: 0
- parent-A advance attacks: 3
- parent-A false accepts: 0
- parent-B advance attacks: 3
- parent-B false accepts: 0
- peer-substitution attacks: 3
- peer-substitution false accepts: 0
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
VALID HIGHER-RECOVERY RANK-PREFIX MERGE AUTHORITY
::
exact-parent specific
+
peer specific
+
merge specific
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
PEER SUBSTITUTION
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
