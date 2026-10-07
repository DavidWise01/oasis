# OASIS Eight-Seam Alignment Report — v26

## Decision

**Keep as a test fixture.**

This one contributes a clean boundary/probe topology, not a new physics law.

## Structural tests

The source's square boundary has:

- 4 edge midpoints
- 4 corners
- 8 unique seams total

The seam set is closed under 90° rotation and reflection: **PASS**

The opposite-seam map is an involution: **PASS**

## Palindromic spine

The source's nested shell sequence reduces structurally to:

`e -> p -> g -> g -> p -> e`

It is an even palindrome: **PASS**

Because it has even length, its center lies between the two middle `g` states rather than on a unique middle element. This is a useful data-structure fact and requires no atom analogy.

## Probe boundary

Using source-normalized radii with box half-size = 1000:

- surface = 1000
- photon = 660
- soft turn = 380
- hard turn = 112
- core = 70

Strict order:

`core < hard-turn < soft-turn < photon < surface`

**PASS**

All 8 seams × 2 probe modes = **16** probe-entry cases were checked.

Core breaches: **0**

Result: **PASS**

Even the source's "hard" probe turns outside the represented core.

## What did not get promoted

The source itself labels the `8 seams <-> 8 crossings` identity speculative. v26 keeps it that way.

No claim was added that:
- a sandbox is literally an atom,
- software layers are electrons/photons/gluons,
- the eight-seam correspondence is a physical equivalence,
- the animation is a scattering simulation.

## What fell out

The useful abstraction is:

`boundary port -> inward probe -> bounded turn -> outward echo`

combined with an eight-port D4-symmetric boundary and a center represented by a join rather than a node.

That is directly reusable as an adversarial probe fixture around the current OASIS HOLD/authority boundary.
