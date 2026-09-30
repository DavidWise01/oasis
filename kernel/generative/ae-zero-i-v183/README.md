# OaSIs Zero/I Canon v183

Canonical root:

    {{0::{i::}}}

Model-local ternary transform:

    -1 -> 0
     0 -> -1
    +1 -> 0&1

This is an information-state transform, not ordinary arithmetic equality.

Lean proves:

- root referent is 0
- each of the three canonical mappings
- inverse round-trip on all source states
- inverse round-trip on all image states
- injectivity
- surjectivity
- bijectivity
- the combined canonical theorem

Files:

- kernel.py
- test_kernel.py
- CANON.json
- proof/OaSIs_Zero_I_v183.lean
- SEAL.json after green CI

Public page:

https://davidwise01.github.io/oasis/architecture/ae-generative-v183/
