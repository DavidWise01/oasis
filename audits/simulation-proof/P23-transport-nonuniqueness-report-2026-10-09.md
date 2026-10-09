# ROOT0 P2.3 — Source-pinned 8-state photon transport: uniqueness countermodels

**2026-10-09; classification: FINITE-MODEL RESULT, NOT PHYSICAL SIMULATION PROOF.**

## Scientific target

Can the frozen ROOT0 AE generative-first v92 phase/identity dynamics, plus a one-photon-dot/8-state local movement constraint, uniquely fix a physical photon trajectory? Test exactly where an otherwise plausible inference introduces freedom that the frozen kernel does not determine.

## Unmodified source

- `DavidWise01/oasis/kernel/frozen/ae-generative-first-v92/kernel.py`: exact original Git blob `bf84cfc8746ccaf35c0204050ada8c3980817cb8`.
- `CANON.json`: SHA-256 `8f2be8951098c7e1764c3c0f5bba982fb3fd8c71f094924b79d0172a313a7bf8`.
- Frozen `advance(Context)` changes phase `q` and generation `g`, seeds identities and digests. There is no physical position, velocity or photon direction in `Context`. The canon explicitly states physical claims are model-local without external verification.

## Candidate additional physical axioms (NOT present in the frozen executable)

1. One logical tick `n=12g+q` increments once per source transition, with a proposed SI duration `τ=ℓP/c` (the former is source-derived; the latter is an interpretation).
2. A transport carrier contains `b∈{0,...,7}` with eight signed corner directions `d(b)=(±1,±1,±1)`.
3. A photon-like object moves one step every tick: integer lattice address `R(n+1)=R(n)+d(b(n))`.
4. Introduce cubic embedding `x(n)=ℓP R(n)/√3` meters, so every individual spatial increment has magnitude `ℓP` and step speed `ℓP/τ=c`. This calibration and diagonal geometry are additional choices, not measured/derived from v92.
5. The extended state projects back onto the **exact** original `Context` each tick, preserving core identity and parent seal. Each transport extension has its own append-only event digest.

These constrain the **size** of every step, not its **direction update**. The frozen code does not implement `b(n+1)`.

## Two constructive countermodels

- **A: straight**: `b(n+1)=b(n)`. With initial b=0, every step is `(1,1,1)` and `R(n)=(n,n,n)`. Net displacement is `nℓP` and the mean velocity is c along one of eight possible diagonals.
- **B: rotate8**: `b(n+1)=(b(n)+1) mod 8`. Every step still has norm `ℓP`, but each consecutive 8-step cycle visits every signed corner once; `Σ_{b=0..7} d(b)=0`. The net displacement after eight steps is **exactly zero**. All eight starting phases were tested.

Both laws use the exact same unmodified ROOT0 core, 12-phase clock, 2³ carrier, nonzero movement each tick, Planck-scaled local step, and append-only history. Neither has been shown to be a physical photon. The circular variant contradicts sustained freely propagating light if treated as a literal vacuum photon, so observational physics could reject it. Its purpose here is to establish that the SOURCE ALONE does not exclude it.

## Executed checks

- Ran 12,288 successive original `advance(Context)` steps for **each** extension (24,576 source advances). Every core state, parent seal, `12g+q=n`, and per-tick displacement matched the claimed contract; 0 violations.
- All 12,288 extended event hashes differ between the two laws, while all ROOT0 lineage hashes remain identical.
- At 12,288 steps / 1,024 twelve-phase cycles, A ends at `R=(12288,12288,12288)` and B ends at `(0,0,0)`; A net displacement ≈`1.986054144e-31 m`, B exactly `0 m`, same externally calibrated elapsed time `6.624763535579004e-40 s`. Both have locally prescribed step speed c. This is a **toy Planck-scale comparison**, not a photon time-of-flight experiment.
- Full 8-state initial-bit sweep confirmed all eight straight trajectories and eight closed rotate8 orbits over eight steps.
- The direction set is **not exactly rotationally invariant**: rotating its `(1,1,1)` vector by 45° about z yields `(0,√2,1)`, which is not a signed-corner vector. A finite set of allowed microscopic classical directions cannot itself equal the continuum of SO(3) rotations of a nonzero vector. Emergent effective isotropy, quantum superpositions, and alternative 8-state interpretations are NOT ruled out.
- Original frozen code remains unchanged; source integrity was checked via Git blob and canon SHA-256.

## Mathematical conclusion (what was proven)

Let `T(s)` be the source-defined logical update. For two external direction policies `F_A,F_B` define `T_A(s,R,b)=(T(s),R+d(b),F_A(b))` and `T_B(s,R,b)=(T(s),R+d(b),F_B(b))`. The projection `π(s,R,b)=s` satisfies `π∘T_A=T∘π=π∘T_B`. Both respect the stated local carrier axioms but exhibit different long-term physical predictions. Thus those axioms and T do **not** uniquely determine a physical photon trajectory.

It would be invalid to claim a unique photon dispersion relation, a particular lattice symmetry, or actual simulation of the universe from this result. To advance the user’s win condition, we must add an independently defensible invariant transport operator, ideally an electromagnetic/quantum gauge evolution and a physical coordinate/measurement map, then test precise predictions versus Maxwell/QED/relativity, including Lorentz constraints.

## Lean and reproducibility

`P23TransportUnderdetermination.lean` captures projection compatibility, distinct direction-update policies, exact eight-corner cancellation, and failure of rotational closure. **Lean 4 is not installed in the local runner**, so this is an uncompiled proof draft; do not upgrade its status without CI logs. The Python source is executable and was tested in a local pinned-source directory. `p23-results.json` is machine output, not a physical dataset.

## Next gate P2.4

Find **the smallest externally defensible direction update** that avoids an eight-step closed orbit while preserving symmetry and electromagnetic physics. Prove its observable consequences and compare with a physically grounded null, rather than fitting a free transport law after seeing data.