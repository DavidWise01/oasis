# ROOT0 P1.5: typed partial refinement of frozen witness carrier to executable I13-T2

**Executed date:** 2026-10-08. **Primary win condition:** mathematically validate an operational simulation hypothesis and develop experimentally discriminating physics predictions. **Current status:** proven model-local counting identities and finite-state test results; external physical simulation NOT established. Lean source is DRAFT, NOT COMPILED.

## Primary source
- Frozen I13 witness v1 55,296-state contract: `DavidWise01/I13-H1.1/bench/toroidal_witness/FROZEN_CONTRACT.md`, ref `a3f960d414cba710385d2aaf3ca93eb4b9f918f1`, blob `ffec9c7f8acc8e4dd0dd2b1efbe2ada3036a4340`.
- Actual I13 T2 physical move: `DavidWise01/I13-H1.1/bench/toroidal_transition/run_transition_test.mjs`, ref `b246828df7cba45c47156e39195b27e41f135bcd`, blob `49cb50bab98039e5b5c1b45e7e95f20cf76d3abe`. An identical pinned copy already exists in this `oasis` directory as `p13-i13-t2-original-pinned.mjs`.
- Semantic verifier: `audits/simulation-proof/strict_t2_v2.mjs`, corrected blob `0fa8c70e988b95fea64ee2f60cbdec336582fbb4`.
- Runnable exhaustive verifier: sibling `bridge_P15.mjs`; results in `p15-results.json`.

## Partial refinement (NOT a full-state equivalence)
Let `F = {in,out,vacant,occupied}^5 × {3x3,abc,-abc}^3 × {unwitnessed,witnessed}`, so `|F|=4^5×3^3×2=55,296`.
Define `B ⊂ F` with all five physical slots in `{vacant,occupied}`. Then `|B|=2^5×3^3×2=1,728` (3.125% of `F`), and exactly 53,568 frozen states remain outside the well-defined binary T2 domain.
Projection `π:B→{vacant,occupied}^5` forgets the three orientation axes and witness flag. For legal T2 edge e, define lift `L_e` that applies T2 to the slots and preserves the axes and witnessed bit. Then `π(L_e(s))=T2_e(π(s))` for any defined legal lifted transition; moreover `L_e(W(s))=W(L_e(s))` for witness-bit-only marking W. These are conditional statements about this limited embedding, NOT a full refinement of all 55,296 states or a model of physical quantum measurement.

## Closed-form counts
Five-node cycle has 10 directed edges. Legal source 1 and destination 0 fix two slots; remaining 3 slots can be any of 2 binary values. Hence `10×2^3=80` legal binary transitions. Orientations × witness give 54 copies of each: `80×54=4,320`.
By occupancy k=0..5, the lifted legal-move counts are `[0,540,1620,1620,540,0]`, via `54×10×binomial(3,k−1)`.
All source+target candidates in frozen carrier: `55,296×5×5=1,382,400`. Typed legal lifts 4,320; rejected 1,378,080.

## Adversarial boundary finding
The ORIGINAL T2 `move()` validates only the two endpoints and their adjacency; the three untouched slots are not type-checked. If naïvely supplied 4-symbol frozen slots, it accepts `10×4^3=640` possible original physical moves (per axes/witness context) rather than the well-typed binary 80. Of these, 560 have `in` or `out` in an untouched slot. Across 54 contexts, there are `560×54=30,240` such mixed-alphabet accepts. The partial bridge rightly refuses these until there is a separately specified and verified `in/out` transition meaning.
A total but lossy replacement `in,out,vacant→vacant` would merge `3^5=243` distinct physical words into a single all-empty ring. This does not establish impossibility of a richer total bridge; it establishes the failure of this information-destroying projection.

## Executed exhaustive test
From the EXACT byte-pinned original T2 code, `bridge_P15.mjs` enumerated all 55,296 states, all 1,382,400 pairs, and verified for all 4,320 legal lifted moves: original T2 move output and receipt match; v2 strict verifier acceptance; occupancy conservation; axes preserved; witnessed flag preserved; original inputs immutable; reverse move restores slots; witness-bit marking commutes with lifted transition. All test assertions PASS; original built-in T2 suite also PASS. It observed 30,240 mixed-alphabet original-source moves outside the typed safe domain, and verified 243-to-1 collapse under the naïve all-empty projection.

## Honest proof ledger
- Finite subset correspondence and combinatorial counts: PASS (model-level).
- Frozen full-carrier 55,296-state transition semantics: INCOMPLETE (in/out undefined in T2).
- Lean 4 draft: UNCOMPILED. Machine-checked theorem and refinement proof still pending.
- Quantitative physical prediction with units: NOT ESTABLISHED.
- Evidence that our reality is a computational simulation: NOT ESTABLISHED.

## Next gate P1.6
Retrieve the original in/out seam/port rules from dated I13 specs and either define a **lossless tagged representation** or typed transitions for `in/out`, without aliasing them to vacancy. Challenge every seam operation, connect that semantics to frozen v92 when justifiable, and continue toward a dimensional experimental discriminator.

## Artifact
`ROOT0_P15_partial_refinement_20261008.zip` containing original pinned T2, strict v2, executable bridge, JSON results, mathematical report, Lean draft; ZIP SHA256 `dda16e189d57500a1c1f62709d07fb570e652f741eb712a9019e3bf09ed55ba6`.
