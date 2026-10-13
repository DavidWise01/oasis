# OASIS / KET · `{{i & dd}}` Reversible Gate ISA v0.3

**Status:** Local JavaScript reference implementation; deterministic quantum-circuit *simulation*. The existing frozen KET/isomorphic kernel and `{{d}}` v0.1 source are unchanged.

## What this release adds

- Compiles each lane-qualified `{{i}}` address into one of ten gate operations: `X H Z S SDG T TDG CX CZ SWAP`. The address ordinal selects the operation modulo 10; target and (when needed) control qubits derive deterministically from the ordinal. The source view and the two diamond projection views do **not** alter gate semantics.
- Validates and retains twin carrier invariant `decode(d+) = reverse(decode(d-)) = i` before compilation.
- Binds the compiled instruction stream to the upstream `{{i}}` identity seal and two-rail witness using a derived SHA-256 program digest. SHA-256 hashes here are tamper checks, **not signatures** or evidence of independent observers.
- Executes a complex-amplitude three-qubit pure-state circuit on ordinary CPU JavaScript, and runs the formally inverse circuit to recover the input state. No irreversible measure instruction appears in the gate ISA.
- Publishes an example GHZ preparation (`H(q0); CX(q0,q1); CX(q0,q2)`) with outcome probabilities 50% `|000>` / 50% `|111>`.

## Architecture

```
{{i}} / 42 address coordinates
       |
       +-- validate {{d+}} :: |.|.|.| --+
       +-- validate {{d-}} :: |.|.|.| --+--> {{i & dd}} witness
       |                                      |
       +-- address ordinal --> gate ISA ------+--> 3-qubit statevector
                                                     |
                                           reverse inverse gate list
                                                     |
                                           original state recovered
```

The `4/3` frame has four vertex addresses connected by three explicit link operators. Geometry is a symbolic projection, not a nanofabricated diamond or diode. The `i_branch` qubit is a logical branch bit, distinct from the original 42-token `{{i}}` identity register.

## Usage

Requires Node.js 22+, no external dependencies:

```bash
node benchmark.mjs
```

The test reports **8,299 passing assertions** across **2,688 token/source-view/destination-view cases**, the 42-address, 22-cell dual-rail example, all ten gate inverse paths, structural integrity/tamper checks, and a three-qubit GHZ preparation. Largest full-program inverse recovery error was approximately `7.77e-16` in this reference run.

Core functions are exported from `gate-isa.mjs`: `mapAddress`, `compileTwin`, `verifyProgram`, `applyGate`, `executeInstructions`, `inverseInstructions`, `executeTwin`, `probabilityDistribution`, `reducedDensity`, and `purity`.

`processor-example.json` and `benchmark-results.json` contain this build's unmodified output. A high-definition editable SVG (`i-dd-gate-isa-blueprint-4k.svg`) and preview PNG are included. `make_blueprint.py` regenerates both (PNG requires CairoSVG).

## Boundaries

The benchmark verifies the math and deterministic software operations, not physical entanglement, coherence, quantum advantage, or quantum-device implementation. Because this is a three-qubit pure-state simulation, the processor can demonstrate Bell/GHZ-like non-product statevectors mathematically; it does not establish a real-world quantum computer. There is no quantum error-correction or fault-tolerance claim.

## Suggested next production target

Build the typed gate IR + full instruction serialization and versioned, append-only gate-run records; add reproducible backend cross-validation against a second independent statevector implementation before any hardware/backend interface is considered.