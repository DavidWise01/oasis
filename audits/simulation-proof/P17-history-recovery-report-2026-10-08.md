# P1.7 — Retained action restores recoverable time history (ROOT0 I13)

Date: 2026-10-08. Scope: **mathematical model only**. Main win condition remains mathematical and experimental evidence concerning whether physical reality is computationally simulated. That claim is **NOT proved** by this test.

## Pinned original / exact semantics

Source is `DavidWise01/I13-H1.1`, `bench/toroidal_transition/run_transition_test.mjs`, pinned Git blob SHA-1 `49cb50bab98039e5b5c1b45e7e95f20cf76d3abe`; included byte-identical as `p13-i13-t2-original-pinned.mjs`. Test loads this exact file, computes the Git blob hash, executes original built-in tests, and uses the actual original `move` and `verify` functions. The P1.6 proposed scheduler is reproduced unchanged: scan edges `(i,i+1%5)`, `(i,i-1%5)` in ascending `i`, choose the first legal `occupied→vacant` endpoint swap; if no edge is legal, stutter. Preserve in/out untouched spectator values, all three orientation coordinates, witness bit. This is a **modeling choice**, NOT an original total-dynamics freeze, and it does not transport `in/out`.

## Main theorem (constructive)

Let `F : S → S` be the deterministic proposed scheduler and `a : S → A` record its selected directed edge or the `none` marker for a stutter. For legal moved edges `(i,j)` we can reverse `F` by applying the actual original T2 `move` with endpoints swapped `(j,i)`. For a stutter, the previous state equals the resulting state. Define `R` using these cases. For every `s ∈ S`,

`R(F(s), a(s)) = s`.

Consequently the augmented transition `G(s)=(F(s),a(s))` is injective, since if `G(s)=G(t)` applying `R` gives `s=t`. The same logic repeated on a retained action sequence recovers a predecessor chain in reverse. This is **conditional on keeping the action log intact**; no uniqueness of the unlogged physical scheduler follows.

## Executed exhaustive tests

- Full 4^5 × 3^3 × 2 = **55,296** frozen symbolic states checked.
- Original model-local P1.6 scheduler: 24,300 moved states; 30,996 stutters.
- Without action record, only **50,382** distinct resulting states; **4,914** excess preimages. The image-fiber histogram is **45,738** outputs with one source; **4,374** with two; **270** with three.
- With action record, **55,296 unique (result,action) pairs**, zero collisions and **55,296/55,296** exact one-step backward reconstructions.
- Worst case 3 candidate predecessors from identical final state implies at least `ceil(log2 3) = 2` bits of information needed in a fixed binary distinguishing label conditioned on that output. A simple global `none`/ten-directed-edges action vocabulary has 11 options, requiring 4 fixed bits if encoded independently of result; encoding is not optimized.

### Concrete 3-to-1 collision

Same output slots `[vacant,occupied,vacant,in,occupied]`, witness `0`, all axes `3x3` can result from:

1. `[occupied,occupied,vacant,in,vacant]`, selected action `0→4` (seam).
2. `[occupied,vacant,vacant,in,occupied]`, selected action `0→1`.
3. `[vacant,vacant,occupied,in,occupied]`, selected action `2→1`.

Each action is legal under original T2 and first-legal scheduler. The action label restores the correct predecessor.

## Chronological / append-only ledger test

Experimental event body: `seq`, `prevDigest`, `beforeHash`, `afterHash`, `action`, `originalReceipt`; event hash SHA-256 over fixed-order JSON body. Trust anchor is **external assumption**, not provided by a self-declared digest. On the 15-step single-token 5-cycle: physical state at tick 15 = state at tick 0; original v1 receipt at moves 0,5,10 repeats exactly; 15 linked event digests are unique because event sequences/previous hashes differ. Reverse replay recovers initial state. Additionally 401 representative initial states passed a 20-step forward/backward cycle each.

With known starting state and trusted final ledger anchor, seven targeted attacks were rejected: deleted, reordered, duplicated event, changed payload hash, altered digest, changed action, and incorrect anchor. The test also constructed **two different internally valid, recomputed alternative histories** with the same final physical state, from distinct starts. They have distinct external anchors. Without independent trust in a start or anchor, neither hash chain can prove which story physically happened. A secure signature or externally witnessed append-only root is a distinct engineering requirement.

## Formal / physical proof statuses

- Finite executable source-linked forward/backward reconstruction: **PASS**.
- Mathematical injected-action inverse argument: **PROVED CONDITIONALLY by direct algebra**, exhaustive finite check supports premises on the proposed scheduler.
- Lean 4 formal source `P17HistoryRecoverability.lean`: **DRAFT UNCOMPILED**; the generic injectivity theorem should be verified by a real Lean toolchain before calling it machine-checked.
- Actual frozen `in/out` seam transport semantics: **OPEN**; only spectator preservation is modeled.
- Dimensionful physical time/correlation/cost prediction and experiment: **NOT DERIVED**.
- Simulation hypothesis for actual reality: **NOT PROVEN**.

## Next formal gate

Machine-check the abstract injectivity theorem and the finite refinement assumptions against original T2 semantics. Then leave P1-only software checks and define a falsifiable **P2 physical observable with units and an independent conventional-physics null model**, as the necessary next step toward the user's actual win condition.