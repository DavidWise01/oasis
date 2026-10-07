# OASIS Cross-Kernel Fallout Report — v25

## What actually falls out

The strongest new relationship is structural, not physical:

`LAPORTE-DUST: 7^8 = 5,764,801`

and

`Atom Instrument pair-address: (7×7)^4 = 49^4 = 5,764,801`.

That means an 8-digit one-axis base-7 address can be grouped losslessly into four ordered 2D base-7 address pairs.

I exhaustively tested **all 5,764,801 addresses**:

- encode as 8 base-7 digits,
- group as four ordered pairs,
- flatten/re-encode,
- compare with original address.

Failures: **0**

Result: **PASS**

This is a real finite-address equivalence. It is **not** evidence that the two old physical metaphors are the same physical system.

## Nested address bands

The three related two-axis constructions are strictly nested:

`Valence Atom {4,5,6,7,8}`
`⊂ Valence Lattice {3,4,5,6,7,8}`
`⊂ Atom Instrument {2,3,4,5,6,7,8}`

Their branch counts per recursive level are therefore:

- 25
- 36
- 49

The progressively tighter reserved boundary really does reduce the surviving address space.

## Mirror rule

The Atom Instrument quadrant map:

`ul ↔ lr`
`ur ↔ ll`

is an involution: mirror twice returns the original quadrant. Exhaustive four-state test: **PASS**.

## Source discrepancy rule

Atomic Map's visible `0.02` first delta and runtime `1.02` first delta remain deliberately unreconciled. v25 marks this as source discrepancy evidence and keeps it in review. It does not silently "fix history."

## Main authority result

The combined path is now:

`address -> witness -> integrity -> authority`

but the arrows are not equivalences.

In particular:

`witness integrity != durable authority`

and every historical fixture still resolves to HOLD until the current OASIS authority path authorizes a state transition.

## Stress result

- exhaustive pair-address round trips: **5,764,801**
- failures: **0**
- elapsed: **4.248s**

## Conclusion

The old kernels are converging on one useful substrate:

- recursive names/addresses,
- reserved boundaries,
- parity/mirror witnesses,
- append-only transition receipts,
- explicit human/drift authority outside the witness machinery.

That is worth preserving. The particle/element metaphors remain optional labels around the substrate.
