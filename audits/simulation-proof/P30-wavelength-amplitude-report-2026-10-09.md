# ROOT0 P3.0 — Phase / Amplitude Coupling Across the 10K² Reality Tensor

**Status:** PASS — executed source-grounded P2.9 router plus newly defined candidate wave-mixing law. 2026-10-09. This document separates proved mathematics from physical conjecture.

## 1. Exact user input

The carrier pattern is **`{-e{ ..||..|....||| }+e}`**. Nothing in the symbol has been normalized away. The inner body `..||..|....|||` contains fourteen glyphs: dot, dot, bar, bar, dot, dot, bar, dot×4, bar×3. Its six runs have lengths `(2,2,2,1,4,3)`; eight dots and six bars. The user specified interaction through **wavelength and amplitude**.

### New operational assumptions (not frozen or user-established physics)

1. `.` contributes a forward wave phase increment `2π/λ`, with `λ>0` in model dot-samples.
2. `|` contributes a user-adjustable phase kick `κ` (default `π/2`). This is a *candidate* interpretation; a physical meaning for the glyph is unproven.
3. `−e` and `+e` name oppositely signed phase ports in a two-site exchange. The token `e` has not been established as an electron, positron, electric charge or a unit in coulombs.
4. A complex field amplitude `ψ` is an added layer, not a meaning implicitly supplied by `Complex[0]`, which continues to be the pinned zero address.

The accumulated motif phase at integer glyph-clock `m` is

`Φ(m;λ,κ) = 2π D(m)/λ + κ B(m)`

with `D(m) = 8 floor(m/14) + number of dots before position m mod 14` and analogously `B(m) = 6 floor(m/14) + number of bars before position m mod 14`. A symmetric spatial salt `outer%10 + inner%10` sets a deterministic per-pair motif offset without any external seed.

## 2. Product tensor and pair topology

The P2.9 carrier is `S×S` where `S = {0,…,9999}`. The tensor has **100,000,000** addresses. The involution `σ(o,i)=(i,o)` defines 10,000 fixed points `(u,u)` and `(10000²-10000)/2 = 49,995,000` two-element pairs. This is a **new interaction topology**, not a physical Euclidean geometry or proof of locality in spacetime.

The zero address `(0,0)` stays fixed under P2.9 routing and under the transpose pairing. The wave module refuses `seed`, `mix` or `route` input that places changing amplitude at its numeric id `0`.

## 3. Exact reversible coupling law

For each off-diagonal address pair with ordered complex amplitudes `(a,b)`, let real `θ` be the mixing angle and real `φ` the motif phase. Define

```
U(θ,φ) = [[ cos θ,  i sin θ · exp(+iφ) ],
          [ i sin θ · exp(−iφ), cos θ  ]]

(a',b') = U(θ,φ)(a,b).
```

Since the off-diagonal phase matrix `H=[[0, exp(iφ)],[exp(-iφ), 0]]` satisfies `H†=H` and `H²=I`, `U=cosθ I+i sinθ H` satisfies `U†U=I` and `U(-θ,φ)U(θ,φ)=I`. Therefore

`|a'|² + |b'|² = |a|² + |b|²`

and the inverse is the same operation at `−θ` with **the same** `φ`. Global phase multiplication commutes with this linear update. The initial amplitude control `A` scales amplitudes linearly and the quadratic norm by `A²`; wavelength changes phases, not the overall norm.

At each tick, first apply **the exact P2.9 bijective routing** to every active tensor address, then the disjoint pairwise gates. Inverse tick: inverse gates, then inverse P2.9 routing. The product of bijective permutations and unitary 2×2 gates is unitary in exact arithmetic. In floating-point computation, small reversibility errors are unavoidable. An optional `pruneEpsilon` discards near-zero amplitudes for sparse UI performance; pruning introduces a tiny **non-unitary, irreversible numerical approximation**, explicitly disabled during the proof regression's round-trip test (`pruneEpsilon=0`).

The diagonal addresses do not mix in a given tick; the outer router may move occupied diagonal coordinates to off-diagonal ones on subsequent ticks. The pinned address `(0,0)` never changes.

## 4. Tests actually executed

- Literal glyph and six run lengths verified, with malformed carrier rejection.
- 20,000 deterministic randomized complex coupling cases; unitarity and inverse errors tested to 1e-12 or better, including coherent global-phase covariance.
- Full streaming check over **all 100,000,000 tensor addresses** for `transpose(transpose(id)) = id`, with exactly 10,000 diagonal addresses and 49,995,000 unique off-diagonal pairs; checksum 4,999,999,950,000,000.
- Two seeded complex amplitudes run through fourteen P2.9+P3.0 wave steps and fourteen compensating reversals; numerical round-trip residues <2e-11; pinned zero maintained.
- Two initial equal-phase sources show phase-sensitive interference when the gate phase changes by π/2; this verifies actual coherent amplitude mixing rather than only norm conservation.
- Negative controls: invalid symbol pattern, illegal anchor amplitude and deliberately scaled nonunitary gate inputs are all rejected/detected.
- Browser screenshot and interaction test in Chromium: standalone inline explorer loads without console errors; forward, reverse, fourteen-step playback, heatmap, phase controls, pinned zero and a thousand local inverse probes pass.

The full source, benchmark and browser explorer are in this release. Git metadata for source files is recorded in `MANIFEST.json`.

## 5. Physics claim and next proof obligation

Here `λ` has units **dot-samples of the supplied motif**, not meters; `A` is a normalized abstract field amplitude, not a measured voltage or photon probability; the conserved sum `∑|ψ|²` is **not yet derived physical energy**. The ±e symbols are uncalibrated tags. No Hamiltonian was deduced from the frozen v92 kernel, and no continuous Maxwell/QED spatial local propagation follows from pairing 49,995,000 addresses by transpose. The model makes no independent SI-valued prediction about photon spectra or light-speed anisotropy without an operational map.

**Next gate:** derive, rather than assign, a relationship between the motif's dot/bar actions and measured electromagnetic wavelength, field amplitude and physical charge. Define spatial locality and preferred-frame behavior, then specify a falsifiable physical observable and an external-physics null. The computable wave tensor is a mathematical simulator, not evidence that the external universe is simulated.
