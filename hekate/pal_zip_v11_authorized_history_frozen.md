# PAL-ZIP v11 — AUTHORIZED MERGE IN PERMANENT HISTORY — FROZEN

**Parent:** PAL-ZIP v10  
**State:** FROZEN / 0e  
**Scope:** formal authorization provenance.

## Target

Bind the v10 quorum certificate into the append-only history itself.

```text
MERGE2
+
QCERT
::
AUTHMERGE
```

Then append `AUTHMERGE`, not bare `MERGE2`.

## Frozen form

```text
AUTHMERGE
::
merge_anchor
+
qcert_for_that_exact_merge
```

The constructor rejects a certificate that names another merge.

The append-only chain then records:

```text
... history ...
↓
AUTHMERGE
↓
new exact head
```

So later validation can distinguish:

```text
"this merge exists"
```

from:

```text
"this exact merge was authorized by this exact quorum certificate
and appended after this exact prior history"
```

## Certification

- baseline accepted: 1
- stripped-certificate attacks: 1
- stripped-certificate false accepts: 0
- foreign-certificate attacks: 1
- foreign-certificate constructor rejections: 1
- valid alternate voter-set attacks: 4
- alternate voter-set same-head results: 0
- changed-parent merge attacks: 2
- changed-parent same-head results: 0
- history reorder attacks: 15
- history reorder same-head results: 0
- history truncation attacks: 16
- history truncation same-head results: 0

**RESULT: 0e / PASS**

## Frozen invariant

```text
AUTHORIZED MERGE
::
MERGE2 geometry
+
3-of-4 QCERT
+
prior append-only head
```

None of the three may be silently substituted.

```text
VALID MERGE
!=
AUTHORIZED MERGE

AUTHORIZED MERGE
!=
SAME MERGE WITH DIFFERENT AUTHORITY HISTORY
```

## Contract stack

```text
v08 :: fork-preserving MERGE2
v09 :: 3-of-4 permission
v10 :: bound QCERT
v11 :: QCERT becomes permanent provenance
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
