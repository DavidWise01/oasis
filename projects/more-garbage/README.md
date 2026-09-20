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

`+sort` is the ordinary sort operator in this riff.

`Ag` is the standard chemical symbol for silver; here it is used as the project's compression pun/token. `MR FUSION` is a Back to the Future reference used as the project motif, not a claim of a physical fusion device.

## Status

```text
phase     = riff / scaffold
frozen    = false
Lean      = Oasis.MoreGarbage.00 candidate
runtime   = more_garbage.py
fixed     = 11/11 PASS
synthetic = 60/60 PASS
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


## Archimedes drill — `A::xx`

`A::xx` is the feed-forward deletion edge.

```text
FAIL
 ↓
rm
 ↓
DELETE CURRENT
 ↓
FREE SPACE
 ↓
ADVANCE
 ↓
NEXT
```

Canonical law:

```text
delete means delete
delete means move forward
no retry
no backtrack
no carry
```

The drill removes the current obstruction and continues through the stream.


## Executable v00

The first reversible mojibake runtime is now wired:

```text
+verify → +sort → +verify → compress → expand
   any NO → rm / A::xx → delete → free → advance
```

The chosen repair must invert back to the exact garbage input. It is not accepted because it merely looks plausible.

Local runtime tests before publication:

```text
fixed mojibake corpus  11 / 11 PASS
synthetic roundtrip    60 / 60 PASS
```

Files:
- `more_garbage.py`
- `ALGORITHM.md`
- `benchmarks/`
- `../../lean/Oasis.MoreGarbage.00.lean`

The Lean module proves the five-gate routing law and A::xx delete-and-advance semantics. It is fresh and remains pending user `0e` compilation.


## v01 correction — primitive scope

v00 tested whole strings. That was the wrong scope for this engine.

Current model:

```text
i = one current primitive

right?
├── Y → +1 → move on
└── N → (0,0,0,-1) down
          ↓
       local search / recursion cost
```

For `Mona`:

```text
M → Y → +1
o → Y → +1
n → Y → +1
a → Y → +1
```

A failed alignment pays the search cost. The base walk is linear `n`; searching down across a bounded local neighborhood gives the structural `n · n = n²` worst-case model.

The corrected runtime is `more_garbage_v01.py`. It searches only when the current primitive answers NO, and a successful local search must distill the corrupted cluster to exactly one output primitive.

Primitive-scope regression:

```text
6 / 6 PASS

Mona                                              → Mona
cafÃ©                                             → café
cafÃƒÂ©                                           → café
K√∂nig                                           → König
The Mona Lisa doesnÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢t ...       → The Mona Lisa doesn’t ...
caf�                                              → caf   [rm failed primitive, advance]
```

Fresh Lean descendant: `Oasis.MoreGarbage.01.lean`, pending user `0e`.

v00 remains provenance and is superseded on **scope**, not erased.
