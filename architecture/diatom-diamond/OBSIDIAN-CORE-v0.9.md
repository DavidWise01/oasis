# OASIS / KET — OBSIDIAN CORE / v0.9

## Boundaries

**Frozen v0.7 floor preserved byte-for-byte.** Manifest: `frozen/dual5-floor-v0.7/FLOOR-MANIFEST-v0.7.json`, pinned SHA-256 for `dual5.mjs`: `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`.

**v0.8 quantum state model unchanged.** `quantum-dual.mjs` is copied from the prior release, and invokes the frozen dual permutation floor. Finite local slices n=2..16 are a resource bound of the CPU reference simulator, not a cap on the symbolic language.

**v0.9 is an additive OBSIDIAN CORE floor overlay, not a mutation or new freeze of v0.7.** A faceted black-glass center visualizes the shared identity and witness, surrounded by two five-pass diamond rails. Obsidian is an amorphous volcanic glass, **not a crystal with a repeating lattice**. The faceting and illuminated surface are symbolic 3D design choices, not claims about obsidian providing qubits or entanglement.

## Quantum noise model

Apply the global isotropic-depolarizing channel to a pure maximally entangled two-register n-level state (constructed by QFT + CADD in v0.8):

`rho(p) = (1-p) |Psi_n><Psi_n| + p I / (n*n)` for `0 <= p <= 1`.

The frozen floor local permutations `P+ tensor P-` preserve pure-state entanglement. They are **not** themselves entangling gates. The new density operator models *global* depolarizing noise, not an assertion about natural obsidian or hardware noise.

| Metric | Formula |
| --- | --- |
| Joint Hilbert dimension | `n^2` |
| Fidelity to ideal output | `1-p + p/n^2` |
| Joint purity | `(1-p)^2 + (2p-p^2)/n^2` |
| Negativity (partial transpose) | `(n-1)/2 * max(0, 1-p-p/n)` |
| Logarithmic negativity (bits) | `log2(2*N+1)` |
| Exact isotropic separability threshold | `p >= n/(n+1)` |
| Reduced state | `I/n` for all `p` |

The reduced von Neumann entropy is `log2(n)` even **after** noise destroys entanglement; it is **not** a valid entanglement measure by itself for this mixed state. Use negativity instead.

Example: `n=13, p=0.10`, negativity `5.353846153846154`, logarithmic negativity `3.5493848304750912` bits, joint purity `0.8111242603550296`, fidelity `0.9005917159763314`. All are computed simulation metrics.

## Run

Requires Node.js 22 (to import frozen JSON with `with {type:'json'}`) and Python 3 + NumPy for the independent reference oracle.

```sh
node frozen/dual5-floor-v0.7/benchmark.mjs
node obsidian-benchmark.mjs
python independent-oracle.py
```

Open `obsidian-threejs.html` in a browser. A full Three.js WebGL renderer loads via CDN when allowed. The self-contained browser document has a functional offline Canvas fallback, which was tested in Chromium by injecting its HTML because direct file navigation was restricted in the test environment. Live Three.js import from CDN was **not** verified in the restricted browser environment.

Controls: four- or thirteen-level slice, isotropic noise 0-100%, five-pass timeline 0-60 per rail, playback, separate rail/core/floor layer toggles, reset camera.

## Security / provenance

The SHA-256 core witness hashes the frozen floor source digest, frozen identity and receipt, token digest, generation, simulation state parameters, and local permutation maps. It is a deterministic integrity marker, **not** a signature, witness independence proof, quantum-mechanical measurement, or cryptographic commitment against a party who controls the input.

Release style: additive `architecture/diatom-diamond/` source. Floor v0.7 frozen. v0.9 is a versioned proposal for the next floor, and may be explicitly frozen as its own revision after review.
