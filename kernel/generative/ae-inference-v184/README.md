# OaSIs Deterministic Inference Engine v184

Append-only inference layer for sealed v183.

## Core rule

Nothing is inferred without:

1. an explicit axiom, and
2. an explicit rule whose premises unify with known facts.

The engine then runs deterministic forward chaining until no new facts can be
derived.

## v183 adapter

The sealed root remains:

    {{0::{i::}}}

Imported symbolic mappings:

    ternary(-1)  -> image(0)
    ternary(0)   -> image(-1)
    ternary(+1)  -> image(0&1)

and the Lean-proved inverse mappings are available as inference rules too.

## Generic rules

Variables start with ?:

    parent(?x, ?y)
    parent(?y, ?z)
    ----------------
    grandparent(?x, ?z)

Every conclusion variable must already occur in a premise, so rules cannot
invent unnamed entities.

## Provenance

Every fact has a SHA-256 receipt.

Derived receipts bind:

- conclusion
- rule ID
- premise atoms
- premise receipt hashes

Tampering with a proof or premise breaks audit.

## Exhaustive v183 test

All 64 subsets of the six v183 source/image atoms are used as seeds. For each
subset the engine:

- saturates to the exact expected closure,
- reaches a fixed point,
- produces the same closure seal under reversed input order,
- passes provenance audit.

Additional tests cover variable unification, unsafe-rule rejection, and proof
tampering.

## Run

    python engine.py --demo
    python test_engine.py

A JSON problem can also be executed with:

    python engine.py --problem problem.json
