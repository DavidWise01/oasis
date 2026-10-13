# {{i & dd}} — v0.6 encoding duel: which encoding naturally fits the mirror?

**Winner for native mathematical geometry: three 13-level qudits.**

This package compares two faithful Hilbert-space representations of the *same user-defined* symbolic 13×13×13 lattice, not a hardware benchmark. The exact source sequence is `00 11 23 35 48 51 55 55 51 48 35 23 11 00`, providing 13 ordered transitions, a midpoint `55→55` seam, and left and right registers `a–m` / `n–z`.

| Dimension | 3 qudits (13 levels each) | 12 qubits |
|---|---:|---:|
| Basis capacity | 2,197 | 4,096 |
| Used sites | 2,197 | 2,197 |
| Padded unused basis | 0 | 1,899 |
| Utilization | 100% | 53.6376953125% |
| Dense complex128 statevector | 35,152 B | 65,536 B |
| Hilbert-space basis representation | three factors of dimension 13 | twelve factors of dimension 2 |

The qudit mirror is the factorwise operator `M(e,l,r)=(12-e,r,l)` — a 13-level transition-register reflection and a swap of the two 13-level letter registers. The binary encoding uses the same flattening `169e+13l+r`, represented in 12 bits. To obtain a **unitary on the entire 12-qubit Hilbert space**, the 1,899 invalid basis vectors are kept unchanged by mirror, seam-phase, and 13-point Fourier operations. That choice is an explicit extension, not a physical gate decomposition.

Benchmark `encoding-benchmark.mjs` performs exhaustive address reversibility and mirror symmetry checks, numerical norm and inverse tests, a seam-local phase flip, a 13-point QFT on one register, and equal-amplitude coherent mirror-pair probes. `independent-oracle.py` cross-checks the mirror, local reduced-state entropies, and QFT with NumPy; it does not call the JavaScript routines. The benchmark suite passes 22,506 assertions. The Python oracle passes. An ideal constructed mirror superposition `(|0,0,1>+|12,1,0>)/sqrt(2)` has 1 bit of entanglement entropy in each of its three qudit single-register reductions. This is a **prepared example**; the symbolic geometry alone does not confer entanglement.

**Caution on time benchmarks:** local Node.js median wall-clock measurements on 100 mirror passes are variable and sometimes slightly favor the padded binary buffer. They are implementation-dependent software timings and **not** evidence that binary or qudit hardware is faster. Both encodings are mathematically equivalent on their 2,197-dimensional valid sector. Hardware choice is unresolved without access to real qubit/qudit processors, native gate error rates, connectivity, circuit compilation, and error-correction overhead. Neither physical entanglement nor quantum computational advantage has been demonstrated.

Open `encoding-duel-threejs.html` for a WebGL view; it requires CDN access to Three.js r0.166.1. If blocked, a clearly marked offline 2D projection is displayed instead. The viewer is informational; computation/benchmark runs in Node.js and Python, not in a quantum device. Select an encoding and mirrored point to compare geometric basis use.

Run:

```sh
node encoding-benchmark.mjs --json benchmark-results.json
python independent-oracle.py
```

Frozen KET kernel and prior `{{d}}` / `{{i & dd}}` tracks are unchanged.