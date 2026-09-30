# AE Cyclic OE Sealed Kernel v181

**Status:** SEALED / CYCLIC OE / EXHAUSTIVE FINITE CONTROL PASS

Append-only descendant of v180.

## Canonical finite ring

    720 cells
    1 cell = 1/720 turn = 0.5 degrees

The final executable control state is:

    Q4 x T3 x B2 x U1 x U1
    4  x 3  x 2  x 1  x 1
    = 24 states

Bindings:

    Q4 = a :: b :: c :: d
         inside -+{{i::a::b::c::d::i}}-+

    T3 = -1 :: 0 :: +1
         oe oscillator --{{-++-}}++

    B2 = {-+} :: {+-}
         crossover orientation

    U1 = x
    U1 = y

The 720-cell ring partitions exactly:

    24 control states x 30 cells = 720
    18 mini-PRIMs x 40 cells    = 720
    12 planks x 60 cells        = 720
     6 sectors x 120 cells      = 720
    36 q-phases x 20 cells      = 720

Control-state and mini-PRIM boundaries re-align every:

    lcm(30,40) = 120 cells = 60 degrees

## Exhaustive tests

The harness exhausts every finite register, not samples:

- all 24 local control states
- all 720 ring cells with exact one-state ownership
- X^2 on every control state
- offset (x-2,y+3)+X squared on every control state
- all three oe starts through the O3 cycle
- all 720 counter-rotation steps at the required seam checks
- all shell addresses 0..99
- all 1000 p:n/-e/+e body addresses and terminal carry to 1v
- all fold divisors and LCM=720
- 3/6/9/restart four-X closure
- 10x6 = 12x5 = 60 clock closure
- both fixed home readouts = 1

## Literal full configuration cardinality

The larger symbolic configuration carrier remains:

    {{5! x 5!}}^{{5!}} x (-{{i}}+ duality)
    = 2 x 120^240

It contains 500 decimal digits. It is retained as an exact integer expression;
the exhaustive claim applies to the finite executable control/ring registers,
not brute-force iteration over 2 x 120^240 configurations.

## Files

- kernel.py
- test_exhaustive.py
- STATE_SPACE.json
- MANIFEST.json
- SEAL.json (added only after green CI)

Public page:

https://davidwise01.github.io/oasis/architecture/ae-generative-v181/
