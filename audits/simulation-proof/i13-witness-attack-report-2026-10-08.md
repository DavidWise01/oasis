# ROOT0 Simulation Proof Benchmark P1 — I13 witness attack (2026-10-08)

## The sole goal
Find and mathematically validate candidate ROOT0 laws and eventually test physically discriminating predictions for simulation theory. This is a P1 verification test, **not** proof reality is simulated.

## Pinned original and exact reproduction
Contract DavidWise01/I13-H1.1 @ a3f960d414cba710385d2aaf3ca93eb4b9f918f1; `bench/toroidal_witness/FROZEN_CONTRACT.md` blob ffec9c7f8acc8e4dd0dd2b1efbe2ada3036a4340.
Verifier original at @ 19bf953ec293c7c371ca53a305638a53e30693cc; `bench/toroidal_witness/run_frozen_test.mjs` blob 24869968e3d71dba517169880f02a17cefd72ded.
Exact saved original Node program rerun locally: PASS, observed=55296, verified=27648, unverified=27648, reported mutations=0; SHA256 f0dbbdba8fa760562e4df783f34b7e25e64cd595ec2e4dbcfce913b1baea9b76 matched original frozen contract.

## Attack harness
Source `audits/simulation-proof/i13-witness-mutation-attack-v1.mjs`; independently enumerates all 55,296 typed conceptual states: 4^5 physical combinations × 3^3 orientations × 2 witness booleans.
Tests an actual `observe(s)` function against:
1. (out.physical, out.orientation)=(in.physical, in.orientation);
2. old ledger is prefix of new ledger;
3. out.witnessed=true;
4. original input is not mutated.
Seed ledger with two distinct receipts so overwrite can be detected; observational record appends a new witness receipt.
- Correct observer: 55296 pass / zero failures.
- Poisons exactly first (all-'in', all-'3x3', unwitnessed) state via mutation of out.physical[0]: detected 1 payload failure.
- Poisons exactly same state via edit of first old ledger receipt: detected 1 prefix failure.
- Assertions executed Node 22 and exit 0 **because intentionally bad implementations were successfully rejected**.

## Gap discovered in historical test
Original v1 frozen runner constructs `before` and `after` via identical payload and orientation expressions without invoking a real observer. As such its reported zero mutation failures is true for that enumeration but does NOT, by itself, verify behavior of any deployed observe implementation. The new harness demonstrates how a transition-level test closes that coverage gap. No fault claimed in the frozen contract; no defective live implementation located.

## Formal next step (Lean source DRAFT, uncompiled)
`audits/simulation-proof/I13WitnessProofDraft.lean` defines typed `Payload`, `World`, `observe` and one-step theorems for payload invariance, witness set, ledger append. These are definitional theorems of the newly defined mathematical witness transition, and **Lean compilation has NOT been run (compiler unavailable)**. They must be checked with Lean 4 and linked by refinement proof to frozen implementation before crediting any machine-checked proof.

## Win condition status
P1: finite-cardinality enumeration rerun; mutation testing added; observer refinement / machine-checked proof pending.
P2: no dimensionful physical prediction.
P3: no preregistered distinguishing experimental data.
P4/P5: no empirical model comparison and no proof of an external simulator.
Next target: produce executable transition implementation with explicit observer/witness separation, prove refinement in Lean, then define one operational physically testable new prediction.
