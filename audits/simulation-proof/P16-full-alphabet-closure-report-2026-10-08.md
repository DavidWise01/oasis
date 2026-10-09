# ROOT0 Proof P1.6: Full 55,296-State Tagged Transition Completion
2026-10-08 · Original frozen I13 unmodified · Lean formalization draft UNCOMPILED · simulation-theory reality claim OPEN.

## Original sources (historically pinned)
- `DavidWise01/I13-H1.1/bench/toroidal_witness/FROZEN_CONTRACT.md` at `a3f960d414cba710385d2aaf3ca93eb4b9f918f1`, blob `ffec9c7f8acc8e4dd0dd2b1efbe2ada3036a4340`: four symbol categories in/out/vacant/occupied, three orientation axes, witness bit. In/out are LOCAL physical seam orientations, not added global ports; witness read-only.
- `DavidWise01/I13-H1.1/bench/toroidal_transition/run_transition_test.mjs` at `b246828df7cba45c47156e39195b27e41f135bcd`, blob `49cb50bab98039e5b5c1b45e7e95f20cf76d3abe`. Its move enforces endpoint occupied→adjacent vacant, swaps both, leaves other slots untouched; it already accepts in/out in untouched slots. There is no source definition for moving the in/out marks.
- `bench/toroidal_collision/run_collision_test.mjs` T3 is a two-labeled-token arbitration rule, separate from in/out tag transport.

## Conservative *proposed* completion
Let Σ={in,out,vacant,occupied}; Θ={3x3,abc,-abc}. Full frozen carrier F=Σ⁵×Θ³×Bool with |F|=4⁵·3³·2=55,296.
Define a partial legal directed edge e=(i,j) iff adjacent modulo five, slot_i=occupied and slot_j=vacant. Swap those endpoints; preserve the other 3 slots (including in/out), orientation and witness. The relation is defined on **the full alphabet**, though some states lack a legal edge. This is consistent with source T2's behavior and does NOT define in/out transport.
All four category counts conserved; each legal move reversible if edge retained; witness-bit marking commutes with a fixed legal move.
Separately, a **new scheduler** selects the first legal edge in fixed order; where no edge exists, it stutters. This yields a total deterministic next-state function over 55,296 inputs. It is a model convention, NOT an original frozen dynamic law.

## Exact analytic counts
- 10 directed adjacent edges, fixed occupied/vacant endpoints, arbitrary 4³ choices for remaining slots: 640 physical move records. Include Θ³·Bool = 54 independent contexts: **34,560 lifted legal moves**.
- Binary-only: 80·54=4,320; mixed in/out spectators: 560·54=30,240.
- At occupancy count k, M(k) = 10·C(3,k−1)·3^(4−k) for 1≤k≤4; values for k=0..5: [0,270,270,90,10,0].
- At tag count t among 3 untouched slots, M_tag(t) = 80·C(3,t); [80,240,240,80,0,0].
- Let 4×4 matrix A indexed by Σ have A_uv=0 only for (u,v)=(occupied,vacant) and (vacant,occupied), else 1. Then **trace(A⁵)=574** cyclic words have no permitted move. Hence 450 words have at least one move; multiplied by 54 contexts: 30,996 scheduler stutters and 24,300 scheduler moves.

## Actual executable results (Node.js 22)
- Frozen original Git blob checked byte-for-byte. The original source suite passed.
- Exhaustively checked all **55,296 states**, all **640 source move records**, and **34,560 orientation/witness lifted moves**. Source output and receipts, exact symbol-count conservation, unchanged tagged spectators, unchanged axes, unchanged witness, no input mutation, reverse edge, and witness commutation all PASS. No source mismatches.
- Scheduler commutes with witness marking on 55,296 states.
- **Counterexample: scheduler NOT globally invertible.** Different starting words [occupied,vacant,vacant,in,in] and [vacant,vacant,occupied,in,in] both map to [vacant,occupied,vacant,in,in] under fixed-first-edge selection. The 55,296-state exhaustive image scan found 4,914 additional sources hitting previously seen images. Distinguish locally invertible move records from globally noninjective deterministic scheduler. Neither constitutes evidence that physical spacetime is compressed.
- Independent transfer-matrix enumeration confirms trace(A⁵)=574; the algebraic counts exactly match the brute-force test.

## Proof status and next question
**P1.6 source-conservative full-alphabet closure: PASS as a newly specified mathematical model.**
Original in/out seam-motion semantics still undefined, so full frozen dynamics / AE-v92 refinement remains UNESTABLISHED. Lean sketch present but NOT machine-checked (no Lean compiler installed). No physical observable with units; simulation of the actual universe NOT PROVEN.
P1.7: determine whether an event-annotated state restores reversible history; then P2: dimensional, preregistered prediction against conventional physics, with a falsifier.
Full independently executed package: `ROOT0_P16_full-tag-closure_20261008.zip` (SHA-256 `a2c1eefccf1dcc98da47301dffaef4256ca241e53f89904d5def760258399ee5`), containing original source, exhaustive runner, independent transfer-matrix check, JSON outputs, Lean draft and report.
