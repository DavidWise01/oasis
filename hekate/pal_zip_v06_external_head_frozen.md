# PAL-ZIP v06 — EXTERNAL APPEND-ONLY HEAD — FROZEN

**Parent:** PAL-ZIP v05  
**State:** FROZEN / 0e  
**Scope:** formal append-only provenance anchoring.

## Target

v05 binds:

```text
{{ -i \::/ { e | r } }}
```

into one pair identity.

v06 binds a sequence of those pair identities so prior history cannot be silently changed while an external trusted head remains fixed.

## Exact chain

```text
H[-1]
::
ROOT:-i

H[n]
::
canonical(
  index=n,
  prev=H[n-1],
  pair=PAIR(e[n],r[n])
)
```

The canonical form length-prefixes every component, so parsing is unambiguous.

The exact head is nested rather than compressed:

```text
H[n]
contains
H[n-1]
contains
...
contains
ROOT:-i
```

Therefore any represented change to an earlier entry changes the final exact head.

## External trust rule

```text
APPEND-ONLY LOG
+
HEAD STORED IN SAME MUTABLE PLACE
::
not enough

APPEND-ONLY LOG
+
EXPECTED HEAD ANCHORED OUTSIDE THAT MUTABLE STORE
::
detects recomputed history
```

The external anchor is what gives the head authority.

## Certification campaign

- entries in baseline chain: `32`
- unique prefix heads: `32`
- tamper cases: `190`
- exact-head false accepts: `0`
- exact-head rejections: `190`
- SHA-256 sampled collisions observed: `0`

### Tamper classes

```text
mutate one pair        :: 32 / 32 rejected
delete one entry       :: 32 / 32 rejected
duplicate one entry    :: 32 / 32 rejected
swap adjacent entries  :: 31 / 31 rejected
replay prior pair      :: 31 / 31 rejected
truncate history       :: 32 / 32 rejected
```

**RESULT: 0e / PASS**

## Exact vs compact

```text
EXACT NESTED HEAD
::
injective for the represented canonical chain
::
not compact

SHA-256(head)
::
compact operational fingerprint
::
collision-resistant, not claimed collision-free
```

## Contract stack

```text
v03 :: anchors e
v04 :: anchors r
v05 :: binds e|r
v06 :: binds ordered history of e|r
```

Therefore:

```text
{{ -i \::/ { e | r } }}
        |
        +-- exact pair bind
        |
        +-- append-only chain
        |
        +-- external trusted head
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
