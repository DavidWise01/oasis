# ROOT0 P2.8 — Complex[0] and balanced ternary floor

**User-defined source input:** `Complex[0]` holds zero in place zero; `0` is the floor; the enclosing floor expression is `{{10x10}}^10`. The earlier `9×1(z)×9(y)` and `{{f{{3.3}}^statespace^^` are retained separately. The meaning of the exponent `^10` is not yet fixed.

## Ordered-edge interpretation (conditional)
The user's coordinate pairs are `-1: (x0,y0),(x0,y-1)` and `+1: (x0,y1),(x0,y0)`. If each pair denotes a directed edge, the path is

```
(x0,y+1) --+1--> (x0,y0) ---1--> (x0,y-1)
```

The **ternary values** balance `(-1)+0+(+1)=0`; the **edge displacements** do not cancel: each displacement is `(0,-1)`, so the two-edge path displacement is `(0,-2)`. There is no conflict: symbolic sign and geometric direction are different quantities. No zeroth transition is assumed; 0 denotes the floor.

## Address geometry
A `10×10` plane contains 100 cells. The earlier `9×1×9` floor contains 81. An optional embedding of a contiguous 9×9 window into a 10×10 carrier leaves 19 cells outside the window and has four placements (offsets `(0,0)`, `(0,1)`, `(1,0)`, `(1,1)`). This embedding **has not been specified by the user** and is not canonical.

An even 10×10 cell grid has no unique centrally fixed cell. Pinning zero is therefore a logical referent or requires an explicit placement rule; the zero cannot be inferred automatically from array geometry. No edge wrapping, spacetime calibration, quantum amplitude, or electromagnetic transition is assumed.

## Ambiguity held open
`^10` could mean ten 100-address floors (1000 address slots), ten independent 100-state factors (`100^10` configurations), or a user-defined nesting operation; these models are mathematically different and **none has been selected**.

The standalone executable and Python benchmark passed their respective assertions. Lean is a draft, not machine-compiled. The frozen AE-v92 kernel has not been modified. No empirical proof of simulation theory follows from the local arithmetic.

**Next semantic gate:** define the exact meaning of `^10` to determine whether the full object is a stack, a Cartesian state product, or a different nesting.
