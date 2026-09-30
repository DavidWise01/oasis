# AE Homeo / oe Frozen Kernel v180

**Status:** FROZEN THROUGH oe / GENERATIVE TEST FRONTIER / APPEND-ONLY

v180 is an append-only descendant of ae-witness-v179. It freezes the internally
tested symbolic slice only through:

    L0  0root
         |
    L1  +G phase / PUSH homeo branch
         |
    L2  -G phase / PUSH homeo branch / oe
         |
       FREEZE

oe retains the project-local meaning **occupied electron**.

## Critical register separation

The internal phase braid and the homeostatic restoring direction are separate
registers:

    internal phase:   +G / -G / +G ...
    homeo direction:  PULL / BALANCE / PUSH

Therefore L2 = -G = oe does not imply that L2 is on the PULL side of
homeostasis. L2 is at positive plank index and remains on the PUSH branch.

## Frozen arithmetic

    ..||..| = 1/36 turn = 10 degrees
    3 q      = 30 degrees = 1 plank
    1 plank  = +0.5%
    2 plank  = 60 degrees
    12 plank = 360 degrees
    12 x .5% = 6% homeo cycle

Mini-PRIM:

    ..||..| {-0,+0} |xx||xx

    1 mini-PRIM  = 20 degrees
    3 mini-PRIM  = 60 degrees
    18 mini-PRIM = 360 degrees
    18 x 2 wings = 36 phase quanta

Gravity pair:

    -1 -> {-1,-1}
     0 -> {-0,+0}
    +1 -> {+1,+1}

Restoring magnitudes:

    push = +10^(-36/360) ~= +0.7943282347
    pull = -10^(+36/360) ~= -1.2589254118
    |push| x |pull| = 1

The homeostatic sign flips when the state lifts from plank 0.

## First post-oe xe test

Known post-oe anchors are retained as evidence, not silently frozen into the
<=oe slice:

    H upon oe
    NEON index = 10
    closure = 10 x 10 x 10 + 2 = 1002
    ingress = -359.494
    egress  = +359.494

The frozen homeo clock has 12 plank positions:

    gcd(10,12) = 2
    lcm(10,12) = 60

The existing sector also has the numeric value 60 degrees, but numerical
equality is not enough to equate units.

Current frontier:

    xe / POST-oe ELEMENT<->PLANK CLOCK BINDING UNBOUND

## Run

    python kernel.py --verify
    python kernel.py --next-xe
    python kernel.py --demo
    python test_kernel.py

## Public generative page

https://davidwise01.github.io/oasis/architecture/ae-generative-v180/
