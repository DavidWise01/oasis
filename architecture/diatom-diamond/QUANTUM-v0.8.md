# {{i & dd}} quantum-state layer v0.8 — atop frozen dual5 v0.7

Immutable predecessor: `frozen/dual5-floor-v0.7/dual5.mjs`, SHA-256 `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`, opcode `UUDDLRLRBASS` × 5 on two rails. **Do not mutate the v0.7 floor.**

## Finite quantum sector

For an n-token input stream (reference demo supports n=2..16), derive two bijections P and Q of token **positions** from the original 60-step positive rail and 60-step negative rail. The unbounded vocabulary is not an infinitely wide quantum state. Exactly n² complex amplitudes are modeled.

1. Start |0,0>.
2. Apply F_n on the left (n-point QFT): (1/√n)Σ_j |j,0> — separable.
3. Apply controlled modular sum: |a,b>→|a,(a+b) mod n> — creates coherent |Φ_n>=(1/√n)Σ_j|j,j>.
4. Apply local P⊗Q from the floor: |Ψ_n>=(1/√n)Σ_j|P(j),Q(j)> — preserves the entanglement.
5. Apply inverse gates to recover the original input state.

For this ideal pure state, reduced purity = 1/n and entanglement entropy = log₂(n) bits. For n=4: 16 amplitudes, 2 bits. For n=13: 169 amplitudes, ≈3.700439718 bits. **The dual floor itself does not create entanglement; CADD is an added gate.** No physical quantum processor or speedup is demonstrated.

## Verification

Locally, v0.7 floor benchmark PASS 1,473; v0.8 model PASS 5,083 assertions over 52 finite slices, including gate reversal, norm, marginals, and separability controls. Independent NumPy linear algebra and SVD PASS at n=4 and n=13. Offline Canvas viewer controls checked in Chromium; a Three.js WebGL network/CDN path has not been independently verified.

Full runnable source, reference Python oracle, manifest, frozen floor archive, benchmark output, and Three.js interactive viewer are supplied in the versioned ZIP release.
