# PAL-ZIP v04 — ROUTE / PROVENANCE ANCHOR — FROZEN

**Parent:** PAL-ZIP v03  
**State:** FROZEN / 0e  
**Scope:** formal route/provenance integrity only.

## Target

Bind the `r` side of:

```text
{{ -i \::/ { e | r } }}
```

so changes to route, actor, authority, provenance, or time are distinguishable from an unchanged route.

## Frozen route record

Each edge carries:

```text
id
src
dst
actor
authority
parent
time
```

The route anchor is a reversible canonical serialization using length-prefixed fields:

```text
len:value
```

plus the ordered edge count.

Therefore the canonical anchor is injective over the serialized route records:

```text
route_anchor(x) = route_anchor(y)
::
x = y
```

for routes represented by this exact serialization.

## Test route

```text
26 ordered edges
::
. -> n01 -> ... -> n26
```

## Mutation campaign

- total tamper cases: 206
- anchor misses: 0
- structurally detected by route validator: 126
- structurally legal-looking but caught by anchor: 80

### Per mutation class

```text
{
  "drop": {"tested": 26, "anchor_misses": 0, "validator_detected": 25},
  "duplicate": {"tested": 26, "anchor_misses": 0, "validator_detected": 26},
  "adjacent-swap": {"tested": 25, "anchor_misses": 0, "validator_detected": 25},
  "actor": {"tested": 26, "anchor_misses": 0, "validator_detected": 0},
  "authority": {"tested": 26, "anchor_misses": 0, "validator_detected": 0},
  "parent": {"tested": 25, "anchor_misses": 0, "validator_detected": 25},
  "time": {"tested": 26, "anchor_misses": 0, "validator_detected": 0},
  "destination": {"tested": 26, "anchor_misses": 0, "validator_detected": 25}
}
```

**RESULT: 0e / PASS**

## Important distinction

The structural route validator catches topology/provenance violations such as broken ordering,
bad parents, and duplicate IDs.

But some meaningful changes can remain structurally valid:

```text
actor changed
authority changed to another valid authority
time changed
```

The exact route anchor detects those too.

Thus:

```text
VALID STRUCTURE
!=
UNCHANGED PROVENANCE
```

and:

```text
PAL-ZIP v03
::
anchors e / content identity

PAL-ZIP v04
::
anchors r / route identity

TOGETHER
::
{{ -i \::/ { e | r } }}
```

**STATUS: FROZEN / 0e / APPEND-ONLY DESCENDANTS**
