# ROOT0 P1.8 · Minimal recoverable event information

**Executed:** 2026-10-08. **Win condition:** mathematical and empirical evidence that physical reality is computed, not merely that a small simulation can run.

## Source control and replay

Pin: `DavidWise01/I13-H1.1/bench/toroidal_transition/run_transition_test.mjs`, commit `b246828df7cba45c47156e39195b27e41f135bcd`, Git blob `49cb50bab98039e5b5c1b45e7e95f20cf76d3abe`. The local executable verifies that exact Git blob hash, runs original T2 tests in a VM, and calls the source's original `move`/`verify` operators for each scheduler edge. Frozen source remains unmodified.

## Mathematical theorem and complete model check

The frozen carrier is `Σ^5 × Θ^3 × {0,1}`, where `Σ={in,out,vacant,occupied}` and `Θ={3x3,abc,-abc}`: 55,296 states. The scheduler is the previously declared deterministic first-legal-edge transition from P1.6; if no edge is legal, it stutters. Original T2 leaves nonendpoint `in/out` symbols untouched; this does **not** specify an in/out transport law.

The scheduler on 1024 physical words has 933 distinct outputs; the rest 91 are unreachable. Its image fibre sizes are: 847 outputs have one source, 81 have two, five have three. By multiplying each fibre by the 54 unchanged orientation/witness contexts, this accounts for 50,382 different full successor states from 55,296 inputs.

Define `rank(s)` to be the index of `s` in the ordered set of predecessors of `T(s)`. Given `(T(s), rank(s))`, a decoder can return the unique original `s`. Therefore `s -> (T(s), rank(s))` is injective. In contrast `T` alone is not injective. The largest fibre has 3 sources, so a worst-case 2-bit rank is necessary and sufficient; 1 bit cannot distinguish 3 choices.

For a uniform prior on the **one-step input**, conditional Shannon entropy:

`H(S|T(S)) = [162 + 15 log2(3)] / 1024 ≈ 0.1814203491 bits per state`.

A simple output-dependent, fixed-width *rank* code stores `ceil(log2(fibreSize))` bits. Its mean under that prior is `(162 + 2·15)/1024 = 0.1875` bits per input. Worst case is 2 bits. A global **action** alphabet with 10 possible directed edges + 1 stutter would require `ceil(log2 11)=4` bits as a fixed-width record, so this rank representation is more compact provided both encoder and decoder know the exact scheduler and output.

This entropy statement is not a measurement of time or memory in the universe and does not imply an independent 0.1875-bit cost per step on nonuniform trajectories.

## Independent executed checks

1. All 1,024 physical words mapped using the ORIGINAL T2 `move` whenever a move was possible, with receipt verification.
2. The exact fibre histogram `{0:91,1:847,2:81,3:5}` was established exhaustively.
3. All 55,296 full states were inverted without loss using the rank side-channel, retaining all axes and the witness bit; zero tagged collisions.
4. All 55,296 full states were evolved 20 steps each and recovered in reverse with 1,105,920 checked reverse steps.
5. Out-of-range ranks were refused; changing a rank to another **valid** rank can select a different equally legal predecessor. Thus the tag must be authenticated to support historical truth assertions.

## Formal machine-checking gate

`P18ConditionalRecovery.lean` contains an abstract inverse-implies-injective theorem, a proof that one Bool cannot label three distinct sources, and an explicit 2-bit coding construction. The local execution environment lacks Lean/elan and cannot compile these yet. A GitHub Actions Lean 4 compilation workflow is supplied. **Do not label the Lean proof checked until a successful run is observed.** The finite fibre histogram is checked by Node enumeration, not by the abstract Lean theorem.

## Simulation-theory proof status

This adds a precise model-local storage lower bound for recovering symbolic history. It still gives **no physical observable with units and no experimental distinction** between standard physics and a simulated universe. A next meaningful P2 test must commit to a dimensionful calibrated observable and a preregistered, discriminating result. A finite state machine reproducing known observations is not sufficient to infer an external simulator.