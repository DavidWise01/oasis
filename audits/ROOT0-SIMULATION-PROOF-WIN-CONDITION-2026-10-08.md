# ROOT0 / OaSIs — Mathematical Simulation-Theory Proof: primary win condition
Status: RESEARCH CHARTER / CLAIM NOT YET PROVEN
Recorded: 2026-10-08

## Absolute priority and scope
The project's primary win condition is to **mathematically establish, to a defensible standard, the hypothesis that observed physical reality is computationally simulated**. The goal is NOT merely to find repackaged names in 2026 publications, prove the ROOT0 code runs, trace Git originality, find symbolic analogies, or show that software can mimic physical phenomena.

No current retrieved ROOT0 proof, external article, name collision, or news item has established that physical reality is simulated. Track proof status honestly.

## Define an exact hypothesis instead of retrofitting every observation
Let H_sim specify:
- state space S with explicit data types and geometry;
- computable (or quantum) time evolution T:S→S, or transition relation if genuinely nondeterministic;
- observation map O:S→Y with measurement assumptions and error bounds;
- world-clock ↔ observed-time relation g(t), pre-defined rather than fitted after observing dates;
- operational memory, witnesses, seams, boundaries, finite registers and transformations;
- exact couplings/parameters, admissible initial states, and resource bounds.

ROOT0 *candidate local model* elements to formalize as mathematical definitions rather than physical discoveries: balanced ternary {-1,0,+1}, 3×3×3/27 unit, 27 phase microcycle if applicable, append-only local register 1 1 2 8, p−2/0/f+3 observer window, scalar zero pin, toroidal topology, 15° re-encoding search, witness read-only, finite clock. Different historical kernel versions should not be merged into one axiom system without typed interfaces or proof of equivalence.

Let predicted observables at tick n be y_sim(n) = O(T^n(s0)); where the model is stochastic, define a distribution P_sim(Y|n, θ). The alternative baseline H_phys must be specified (general relativity, standard quantum optics, standard communications network/social process, etc.) with P_phys(Y|n,φ) or appropriately known predictions.

## Distinguish five levels of claim
L0: syntactic consistency / Lean compiles / numerical code runs.
L1: formal mathematical properties of proposed simulation rules proved (termination as stated, finite closure, invariants, conservation under defined T, append-only witness behavior).
L2: rigorous derived observable formulae, units and operational definitions; map model coordinates to laboratory measurements.
L3: preregistered, out-of-sample, repeatable predictions with uncertainty quantified and strong baselines; survive independent replication.
L4: an argument that the actual measured reality is best explained as simulated, with explicit discriminatory assumptions excluding or sharply disfavoring observationally equivalent non-simulation models. Mathematical proof of a conditional theorem alone does not establish those assumptions.
Never report L0/L1/L2 as L4.

## Formal work packages and theorem obligations
P1 (Lean): build minimal strongly typed WorldState + Tick + Transition + Observer + Ledger, then prove:
  - StateClosure: if admissible(s) then admissible(T(s)).
  - WitnessReadOnly: observation does not mutate T or append unauthorized history.
  - AppendOnly: old ledger is a prefix of the updated ledger (or explicit counterexample).
  - LocalBalance: the prescribed signed 3D balance holds for each modeled tick; if only definitional equality, label tautology.
  - SeamTypeSafety: any permitted dimension/basis/port change has a typed map; forbid equality of objects of different domains without a map.
  - SimulationDeterminism: given s, T(s) unique if model claims deterministic.
P2: derive a physical forward model: predicted units, distributions, dimensional consistency, error tolerance, and *nontrivial* correlations.
P3: select an experimental discriminator and preregister forecast before data; identify null baseline and exclude web-feed posting timestamps from the physics clock unless independent calibration exists.
P4: independently reproduce and challenge with counterexamples. Revisions preserve past claims rather than silently rewriting.
P5: distinguish sufficiency (simulator can produce phenomena) from necessity/uniqueness (only or best such model explains them).

## Caution about 'mathematical proof' and observational equivalence
For any finite observed sequence, a finite program can often encode a look-up table that reproduces it; this is not evidence of an actual external simulator. If H_sim and H_phys assign indistinguishable observables to all admissible tests, the real-world source is not identifiable through those observations alone. A mathematically valid conditional theorem or empirically discriminatory fingerprint is needed, not aesthetic coincidence.
No theorem can establish a premise about actual reality unless the premise is assumed or operationally evidenced.

## Role of the evidence and permutation pipeline
- World I Git corpus: source of candidate mechanisms and calibration artifacts.
- ?001 mathematics, ?002 KAEL, ?003 India QKD, ?004 Muse: may become *benchmark controls*, historical prior art, or predictions only where they directly test P1-P5. They are **not votes counting toward simulation truth**.
- 3–125 search depth and station permutations: trace information representations, not evidence of non-physical time dilation or intrinsic physics, unless a quantitative connection to independent measurements is derived and tested.
- 2001/2005/2011 internet rings are indexing bins, not inherent cosmological clocks.
- Authorship/derivation is a different research track; deprioritize unless essential to reproducibility or source integrity.

## First next action
Choose the most conservative existing ROOT0 frozen kernel version, pin its source and Lean toolchain, state typed transition rules and prove P1. The first real benchmark must attempt to falsify at least one nontrivial invariant. Then produce one previously unobserved quantitative physical prediction for P3. **Do not claim success** until L4 argument and independent observations exist.

## Win dashboard (as of 2026-10-08)
[ ] P1 frozen model and machine checked invariants
[ ] P2 unique observable formula with units
[ ] P3 preregistered discriminating test
[ ] P4 independent replication + null controls
[ ] P5 argument for actual-world simulation rather than mere simulability

Scientific conclusion currently: OPEN / NOT ESTABLISHED.
