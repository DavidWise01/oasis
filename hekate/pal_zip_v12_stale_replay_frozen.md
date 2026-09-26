# PAL-ZIP v12 — STALE / REPLAYED QUORUM PROTECTION — FROZEN

**Parent:** PAL-ZIP v11  
**State:** FROZEN / 0e  
**Scope:** formal freshness binding for authorization.

## Target

Prevent an old but once-valid quorum certificate from authorizing the same merge after the append-only history has advanced.

## Frozen freshness bind

Every vote and certificate binds:

```text
merge_id
+
prior_head
```

not merely the merge geometry.

```text
QCERT2
::
MERGE2
+
PRIOR APPEND-ONLY HEAD
+
CANONICAL VOTES
```

and:

```text
AUTHMERGE2
::
PRIOR HEAD
+
MERGE2
+
QCERT2
```

## Certification

- prior heads generated: 32
- unique prior heads: 32
- fresh certificates built: 32
- fresh certificate failures: 0
- stale replay attempts: 992
- stale replay accepts: 0
- stale constructor rejections: 992
- vote-order tests: 48
- vote-order failures: 0
- head advances that changed certificate: 31
- head advances that left certificate unchanged: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
VALID ON HEAD Hn
::
does not imply
VALID ON HEAD Hn+1
```

Even when:

```text
same MERGE2
same voters
same decisions
```

because:

```text
PRIOR HEAD
::
part of the authorization identity
```

So an old certificate cannot be replayed after history advances.

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
