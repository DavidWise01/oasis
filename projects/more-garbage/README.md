# M.O.R.E.G.A.R.B.A.G.E.

Working project scaffold. Not frozen.

Alias:

```text
NO MORE GARBAGE
```

Riff:

```text
M O | R E | G A | R B | A G | E

MO :: RE :: GA :: RB :: AG :: E
```

Initial operator chain:

```text
`-rem`        MO
`+verify`     RE
`+sort`        GA
`+verify`     RB
`compress to` AG  (Ag / silver)
`expand as`   E++...
```

Compact read:

```text
MORE GARBAGE
   ↓ chunk
MO | RE | GA | RB | AG | E
   ↓ operate
-rem | +verify | +sort | +verify | compress | expand
   ↓
NO MORE GARBAGE
   ↓
MR FUSION riff
```

## Isomorphic repair rule

If two forms preserve the same invariant, the isomorphic language should translate or repair between them without requiring a new manual isomorph declaration.

A new explicit isomorph is only needed when the invariant itself changes.

```text
same invariant + new spelling/order/medium
→ translate

changed invariant
→ declare a new isomorph
```

## Current restraint

`+sort` is is the ordinary sort operator in this riff.

`Ag` is the standard chemical symbol for silver; here it is used as the project's compression pun/token. `MR FUSION` is a Back to the Future reference used as the project motif, not a claim of a physical fusion device.

## Status

```text
phase     = riff / scaffold
frozen    = false
Lean      = none yet
next      = define operator semantics by example
```

## Repair law — isomorph or stop

The recycler does not accept "looks plausible" as repair.

```text
input garbage
  ↓
recover original invariant?
  ├─ YES → ISOMORPHIC
  │          ↓
  │       distill
  │          ↓
  │    AETHER | TEMPORAL
  │
  └─ NO  → UNFIXABLE
```

A candidate is valid only when the same underlying invariant can be recovered inside the bounded system.

If the invariant cannot be recovered, the engine must return **unfixable** rather than fabricate a replacement.

`AETHER` and `TEMPORAL` are preserved here as named recoverable destinations. Their finer distinction is intentionally not inferred in this scaffold.


## `rm` — rejection / free-space edge

`rm` is not one of the five acceptance transforms. It is the failure edge around them.

```text
candidate
   ↓
+verify → +sort → +verify → compress → expand
   │         │        │         │         │
   └── NO ───┴── NO ──┴── NO ───┴── NO ──┴── NO
                       ↓
                       rm
                       ↓
                     delete
                       ↓
                   free space
                       ↓
                 next candidate
```

Acceptance law:

```text
YES ∧ YES ∧ YES ∧ YES ∧ YES
→ may enter next cycle

any NO
→ rm
→ do not enter next cycle
→ free the working space
→ move on
```

The engine does not carry a rejected working object forward for another repair pass.
