# Chemical Mnemonic v185

**STATUS: candidate formal alignment; append-only descendant**

User term:

> mnemonic = chemically persistent/recoverable trace inside a defined time frame.

Formal split:

    Father Time = ordered rings / time windows
    Mother Nature = reuse / hold / release classification
    Trace strength = STRONG > MEDIUM > WEAK > ZERO

Discrete transition:

    STRONG -> MEDIUM -> WEAK -> ZERO -> ZERO ...

Two tethers are kept semantically distinct:

    lineage tether       : ancestor chemistry -> descendant relation
    decomposition tether : source chemistry -> environmental residue

In the executable abstraction they intentionally share the same monotone
recoverability walk. That is a modeling convenience, not a claim that the two
processes have identical real-world kinetics.

## Scientific boundary

Entropy supplies an arrow/direction, not a universal decomposition clock.
Actual chemical persistence depends on molecule/compound, environment, assay,
temperature, water, oxygen, microbes, surface area, combustion, etc.

The formal proof therefore proves only properties of the declared model:
- recoverability rank never increases under degradation;
- ZERO is absorbing;
- STRONG reaches ZERO after three discrete degradation hits;
- time rings have monotone start/end bounds;
- reuse/hold/release classification is deterministic.

## Executable benchmark

kernel.py exhaustively checks every starting strength across stages 0..1000:
4,004 monotonicity cases, plus ring construction, absorbing-zero, classification,
and lineage/decomposition abstraction alignment.

Expected seal:

    0e / CHEMICAL MNEMONIC v185 EXECUTABLE PASS

Lean target:

    proof/OaSIs_Chemical_Mnemonic_v185.lean

The GitHub workflow installs Lean 4.33.1 and compiles the proof.
