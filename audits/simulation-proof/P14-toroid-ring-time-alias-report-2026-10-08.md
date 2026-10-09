# ROOT0 Simulation Proof Gate P1.4: five-node ring, exact transition and repeating-time receipt

**Status 2026-10-08:** exhaustive executable model checking PASS; mathematical witness-alias counterexample ESTABLISHED; Lean DRAFT NOT COMPILED; simulation-theory world claim UNPROVEN.

## Original source and scope
I13 source \`DavidWise01/I13-H1.1\` at commit \`b246828df7cba45c47156e39195b27e41f135bcd\`, \`bench/toroidal_transition/run_transition_test.mjs\`, original Git blob \`49cb50bab98039e5b5c1b45e7e95f20cf76d3abe\`. This exact source is already pinned in this \`oasis\` folder at \`p13-i13-t2-original-pinned.mjs\`. Original test status PASS, exact receipt sha256 \`73cbd8a4ed72dfbde2318bb3b2753d4661aa248ef18261e38389f067576f6767\`.

## Domain and mathematical result
For binary occupancy \`s ∈ {0,1}^5\` on a five-node cycle, legal \`(s,i,j,s')\` moves one occupied source to vacant adjacent destination \`j=i±1 (mod 5)\`, conserving \`∑_k s[k]\`. Reversing \`j→i\` restores the state. The original full 55,296-state frozen witness schema also has \`in,out\` symbol variants, 3^3 orientations, and 2 witness flags; the T2 physical transition is defined only on a 2^5 binary occupancy *subdomain*. No complete refinement map between these separate structures has yet been proven.

## Executed model check
- 32 binary occupancy states × 25 ordered endpoints = **800** transition candidates; **80 legal**, **720 rejected**.
- Legal moves by total occupied population k=0..5: \`[0,10,30,30,10,0]\`.
- **80/80** reversible and occupation-conserving, 80/80 original inputs unchanged; **16** seam-crossings across all binary backgrounds.
- Six independently rehashed illegal message types for each of 80 legal moves: **480/480** pass source \`verify(tx)\` because original is hash equality, **0/480** pass strict semantic transition predicate. This does not break original \`move\` and does not require SHA256 collisions.
- A single occupied token returned to its original physical state after 5 clockwise moves. Repeated same edge at event steps **0, 5, 10** produced **identical v1 transition-receipt SHA256**, because message input is identical. This is event/time aliasing in v1, not a cryptographic hash collision.
- Experimental v2 wrapper includes event sequence and previous digest with semantic validation; observed distinct receipts for 0/5/10, and anchored 15-event transcript rejects replay, deletion, reorder, tampering and wrong final anchor. An attacker can still generate an alternative valid-looking history and rehash it without an independently trusted anchor or signature. A hash chain by itself does not prove which history happened.
- A simple Lean proposition establishing equal generic digests for identical repeating edge inputs appears alongside, but **Lean was not installed and the draft was not machine checked**. Code-source assertions are executed and exhaustively checked only over the defined finite transition domain.

## Link to winning simulation-theory hypothesis
Finite cyclic state closure shows what the proposed simulator can mathematically do, **not** that space-time is discrete or externally simulated. The new concrete proof obligation is: give a typed refinement mapping from \`4^5 × 3^3 × 2\` to executable T2 rules and derive at least one experimentally differentiating, dimensionful physical prediction. Until then no real-world simulation proof follows. The internet/press/name permutation observations do not count toward this proof.

## Artifacts
The current-turn packaged executable sources, original frozen file, Lean draft, tests, machine results and README are in \`ROOT0_P14_actual_ring_temporal_proof_20261008.zip\` (shared conversation artifact, not directly in Git). This Git report and its compact smoke-test source provide stable provenance. Package zip SHA256 \`ebb5a730abcc51dc6a8749b16f4bb261d5b42f5c419fb51ac1530ae2dca0c5a0\`, verification \`testzip=None\`.


## Combinatorial proof of the 80-transition count
On the 5-cycle, there are 10 directed adjacent edges (2 choices at each of 5 source nodes). Fix a directed edge i→j. A legal state must have s[i]=1 and s[j]=0; its remaining three bits are unrestricted. Thus exactly 2³=8 legal pre-states exist per directed edge, yielding exactly 10·8=80 distinct legal (state,edge) transitions. At fixed occupied population k, choose k−1 occupied positions from the remaining three, giving M(k)=10·binomial(3,k−1), hence k=0..5 has counts [0,10,30,30,10,0].
For each move, mass(s′)=mass(s)−1+1=mass(s). Reversing the same edge swaps that same 1/0 pair back, so the move is invertible.
For the single-token orbit s(t+5)=s(t) with clockwise edge e(t+5)=e(t), any deterministic receipt function r=H(s(t),e(t),s(t+1)) satisfies r(t+5)=r(t), regardless of the selected hash algorithm. This is *identity of hash input*, not cryptographic collision or evidence of real-world cyclic spacetime.
