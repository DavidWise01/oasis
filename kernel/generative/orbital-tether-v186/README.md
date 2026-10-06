# OaSIs Orbital Tether v186

**STATUS: append-only descendant / candidate until Lean CI compiles**

## Purpose

Align the existing five-phase closure clock with standard Newtonian two-body
orbital invariants without conflating the symbolic clock with physical motion.

    ORBITAL TETHER
    geometry = r, v
    tether   = gravity / two-body central attraction
    Father Time = 5 exact observation phases
    closure  = completed ring
    memory   = conserved invariants in the ideal model

## Five-phase ring

    . | | | | .
    0 -> 1/5 -> 2/5 -> 3/5 -> 4/5 -> 1 -> wrap 0

In code the five unique phase addresses are 0..4. The fifth transfer returns
to phase 0 and increments the revolution witness by one.

This is an observation/control partition over a continuous orbit. It is not a
claim that a physical orbit jumps between five locations.

## Physics alignment

Standard specific orbital energy:

    eps = |v|^2 / 2 - mu / r

Standard specific angular momentum in the planar benchmark:

    h = r_x v_y - r_y v_x

Ideal conic classification:

    eps < 0  -> bound
    eps = 0  -> parabolic
    eps > 0  -> unbound

## Executable benchmark

kernel.py performs:

1. exact Fraction-based 5-phase closure;
2. modular clock sweep over all 5 starting phases, 17 revolution counts,
   and 101 forward step lengths;
3. bound/parabolic/unbound energy-sign tests;
4. 2,001-point circular invariant sweep;
5. 2,001-point eccentric-ellipse invariant sweep;
6. invariant checks at all five observation phases.

The orbital states for the ellipse are generated analytically through Kepler's
equation, so this is primarily an invariant/formula benchmark rather than a
numerical integrator drift test.

## Lean proof

proof/OaSIs_Orbital_Tether_v186.lean proves:

- every phase index is < 5;
- next phase is +1 modulo 5;
- five steps return any phase to itself;
- ten steps give two closures;
- five steps from each explicitly checked phase increment the revolution witness;
- symbolic negative/zero/positive energy classification;
- the canonical tether witness satisfies the required invariant witnesses;
- the full modelCheck reduces to true.

The Lean layer proves the declared discrete architecture and symbolic energy
classification. It does not yet prove Newton's differential equations,
Kepler's laws, or conservation theorems from first principles.

## Seal target

    0e / OASIS ORBITAL TETHER v186 EXECUTABLE PASS
