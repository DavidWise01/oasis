# OaSIs v180 — Frozen Homeo / oe Slice

## Seal

This revision freezes only the internally tested path through oe.

    L0  0root
     |
     | lift
     v
    L1  +G phase
        PUSH homeo
     |
     v
    L2  -G phase
        PUSH homeo
        oe
     |
    FREEZE

The two gravity registers are intentionally distinct.

## Phase hierarchy

    q := ..||..|
    q = 1/36 turn = 10 degrees

    3q = 30 degrees = one plank step
    one plank step = +0.5 percent

    two plank steps = 60 degrees
    twelve plank steps = 360 degrees
    twelve x 0.5 percent = 6 percent

## Mini-PRIM

    ..||..| {-0,+0} |xx||xx

The right wing is generated exactly by:

    reverse(..||..|) = |..||..
    inverse dots -> x = |xx||xx

Width:

    left q       10 degrees
    zero seam     0 degrees
    right q      10 degrees
    -----------------------
    mini-PRIM    20 degrees

Therefore:

    3 mini-PRIM = 60 degrees
    18 mini-PRIM = 360 degrees
    18 x 2 q-wings = 36 q-wings

## Gravity

Paired ternary carrier:

    -1 => {-1,-1}
     0 => {-0,+0}
    +1 => {+1,+1}

Homeostatic restoring branch:

    plank < 0  => PULL
    plank = 0  => BALANCE at 1 full gravity baseline
    plank > 0  => PUSH

Magnitudes:

    push = +10^(-36/360)
    pull = -10^(+36/360)

Since 36/360 = 0.1:

    |push| x |pull| = 1

The sign flips when the state lifts from plank 0.

## Frozen boundary

    oe = occupied electron

The freeze ends at L2. Post-oe facts are test inputs, not silently promoted into
the frozen <=oe slice.

## Post-oe test

Known anchors:

    H upon oe
    10 NEON
    10 x 10 x 10 + 2 = 1002
    ingress -359.494
    egress  +359.494

Compare the two existing clocks:

    element clock = 10
    plank clock   = 12

    gcd(10,12) = 2
    lcm(10,12) = 60

The model also has a 60-degree sector. That is a numerical match until a rule
establishes compatible units.

Therefore the next fail-closed frontier is:

    xe / POST-oe ELEMENT<->PLANK CLOCK BINDING UNBOUND

No mapping is generated automatically.

## Scope

This is a user-defined symbolic/isomorphic kernel. Physical or chemical terms
inside the notation remain model-local unless independently validated.
