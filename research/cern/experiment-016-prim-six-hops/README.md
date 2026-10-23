# PRIM Experiment 016 — six-hop phase closure

Phase step 0.3367 cycles, correction 0.0101 cycles per three hops. Compared correction at hops 3 and 6 against distributing -0.0101/3 over every step. Exact fractions in Python avoid round-off.

| Hop | Boundary-corrected cumulative cycles | Distributed cumulative cycles | Difference cycles |
|---|---|---|---|
|1|0.3367|1/3|0.0033666666667|
|2|0.6734|2/3|0.0067333333333|
|3|1|1|0|
|4|1.3367|4/3|0.0033666666667|
|5|1.6734|5/3|0.0067333333333|
|6|2|2|0|

PASS: exact closure at hops 3 and 6, with total six-hop phase 2 cycles. Maximum scheduling mismatch 0.0067333333333 cycles (~2.424 degrees). The intermediate sawtooth mismatch repeats every three hops. This is an arithmetic phase scheduling test, not physical photon validation.
