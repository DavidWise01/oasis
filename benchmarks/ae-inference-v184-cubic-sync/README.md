# v184 cubic synchronous-zero test

Canonical invariant:

    seed = 1i
    axes = (x,y:z)
    branches = x+, x-, y+, y-, z+, z-
    cardinal increment = +15
    clock = 5 / 4 / 3 / 2 / 1 / 1 / 0 / 0

Closure is accepted only when all six branches possess terminal(?,7,0)
simultaneously. The harness also rejects early-zero, late-zero, skipped-state,
and missing-branch traces.

Sealed v184 is not modified by this test.
