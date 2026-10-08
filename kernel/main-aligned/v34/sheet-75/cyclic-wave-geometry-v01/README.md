# SHEET 75 — Six-arity register geometry and closure

Append-only successor to SHEET74. The literal user ladder **60 / 15 / 3 / 1 / 1** is modeled as 60 binary-position slots on a cyclic graph `C60` (60 vertices, 60 edges), grouped in 15 packets of 4, then 3 groups of 5 packets, then 1 retained root and 1 SHA-256 commitment. This is an **explicit provisional combinatorial geometry**, not a claim that `decoisohedron` has 60 vertices.

The per-phase operation rotates every bit +15 positions and complements bits (`b XOR 1`). Applying it four times returns the **complete original state**, not just its digest. Packing/unpacking retains all child values and raises an error if the data are altered without a matching digest. Six-arity terminology and 416 symbolic source registry items are retained.

**Locally measured:** 20/20 checks pass; intermediate steps 1–3 differ from initial state, fourth equals initial state exactly. Initial pattern has 29 set bits. Executable GitHub copy is separately committed for independent replay. Numerical gravity dynamics from SHEET71–73 are **not** coupled into this digital proof, so phase-space orbital closure remains open.

Run: `python benchmark.py`. Previously committed numbered sheets are unchanged.
