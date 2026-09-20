# MORE GARBAGE — one-bit delete primitive v00

Scope is exactly **one bit / one primitive**. Do not scale this checkpoint to a nibble, byte, sentence, file, sector, or device.

Canonical walk:

```text
click / trigger

1 :: action a gets flagged for deletion
2 :: flag a
3 :: check flag 1
4 :: check flag 2
5 :: check flag 3
6 :: check flag final
7 :: overwrite = true if flag is still true
     overwrite = false if flag is false
8 :: committed delete unbinds and decoheres
```

Primitive signature:

```text
[ 1 1 2 4 ] . n . n^2
```

One-bit state/search model:

```text
2^3 = 8 cohesion width
2^8 = 256 states per bit
16 lanes
16 × 256 = 4096 local search states
```

Committed path:

```text
a
↓ flag
↓ check 1
↓ check 2
↓ check 3
↓ final check
↓ overwrite = true
↓ unbind
↓ decohere
?
```

If any check clears the deletion flag, overwrite is false and `a` remains bound/coherent.

Lean candidate:

```text
lean/Oasis.MoreGarbage.Prim1Bit.00.lean
```

The Lean module proves the eight-tick schedule, `[1,1,2,4]` shape, 256-state-per-bit user model, 16×256=4096 local search space, flag/overwrite contract, committed `a → ?` path, cancellation paths, and all 16 four-check Boolean combinations.

Status: **fresh candidate; pending user 0e compile**.
