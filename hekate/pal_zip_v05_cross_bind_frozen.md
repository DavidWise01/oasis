# PAL-ZIP v05 — CROSS-BIND e|r — FROZEN

**Parent:** PAL-ZIP v04  
**State:** FROZEN / 0e  
**Scope:** formal content/provenance binding only.

## Target

Close the swap attack against:

```text
{{ -i \::/ { e | r } }}
```

where `e` and `r` may each be individually valid but belong to different records.

## Problem

```text
record A :: eA | rA
record B :: eB | rB

bad recombination
::
eA | rB
```

Independent membership asks only:

```text
is eA in the trusted content set?
is rB in the trusted route set?
```

That is insufficient to establish that the two belong together.

## Frozen bind

```text
EA(e)
::
exact content anchor from PAL-ZIP v03

RA(r)
::
exact route anchor from PAL-ZIP v04

PAIR(e,r)
::
length-prefixed canonical encoding
of {{ EA(e) | RA(r) }}
```

The trusted baseline stores the allowed **pair identity**, not merely two independent allow-lists.

## Certification campaign

Built `64` records with `64` unique content anchors and `64` unique route anchors.

Every wrong cross-combination `ei | rj` for `i != j` was tested.

- correct pairs: `64`
- correct-pair failures: `0`
- wrong cross-swaps: `4,032`
- false accepts under independent membership: `4,032`
- false accepts under trusted pair bind: `0`
- pair-bind rejections: `4,032`

**RESULT: 0e / PASS**

## Certified distinction

```text
VALID(e)
+
VALID(r)
!=
VALID(e|r)
```

The relation itself is contractual state:

```text
e belongs to r
::
must be anchored
```

## Trust boundary

The pair encoding is exact for the represented data, but an active party can recompute a new pair representation.

Therefore:

```text
PAIR ENCODING
::
binds e to r

TRUSTED EXTERNAL ANCHOR
::
binds authority over the accepted pair
```

That external-anchor problem is the next target.

## Root bind

```text
{{ -i \::/ { e | r } }}
```

```text
e :: what crosses
r :: its accountable route
\::/ :: the pair is one contractual record
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
