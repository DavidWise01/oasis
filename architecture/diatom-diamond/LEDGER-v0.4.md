# OASIS / KET — {{i & dd}} v0.4

## Typed gate packet + append-only execution ledger

This software-only prototype extends v0.3 **without changing** frozen KET, {{i}}, {{d}} or the twin-diamond v0.2/v0.3 gate ISA.

The four-port / three-coupler geometry remains `|.|.|.| & |.|.|.|`.

### Interface

1. `createInstructionPackets(twin)` compiles the already-validated twin carriers into exactly one typed gate packet per source address. Every packet binds its source coordinate, opcode, target/control, source view, identity seal, twin-rail witness, program digest, and SHA-256 packet digest.
2. `buildLedger(twin, {initial})` replays the compiled gates, checking each optimized 3-qubit statevector result against a separately coded **dense 8x8 complex-matrix** gate oracle. Each append-only logical entry stores its sequence number, previous head, typed gate packet, input/output state hashes, eight-amplitude output snapshot, oracle deviation, and hash of the full entry body.
3. `verifyLedger(twin, ledger)` deterministically reconstructs the complete execution **from the authoritative twin** and requires structural equality with the supplied ledger. This catches tampering, reordered entries, truncated histories, and replay with the wrong identity/view/generation.
4. The inverse gate circuit must recover the original initial state to `1e-12` max complex amplitude error.

### Scope and cryptographic boundary

- This is a deterministic 3-qubit **classical** quantum-circuit simulator; it does not execute on physical quantum hardware.
- The dense-matrix oracle is algorithmically distinct from the v0.3 optimized pairwise gate path, but runs in the same Node.js process. It is **not an independent third-party implementation** or formal proof.
- A SHA-256 chain makes unexpected changes detectable **relative to an independently retained trusted ledger head or input twin**; hashes alone provide neither authentication nor strong protection against rewriting the entire history.
- No persistent database, server-side transaction log, signature, trusted external witness, or true physical quantum error-correcting code is implemented.
- `buildLedger` uses immutable *logical* append order but returns a normal JavaScript object; consumer code can mutate that object. `verifyLedger` detects differences against deterministic reconstruction from trusted input.

### Verified benchmark (Node.js 22)

- `2815` assertions passed; `2688` single token/source-view/destination-view scenarios.
- `42` typed packets and `42` execution ledger entries in the full stream.
- `30` direct gate/target dense-matrix oracle comparisons (10 opcodes × 3 targets).
- `7` negative tamper and provenance checks.
- full circuit: numerical inverse recovery error `7.771561172376096e-16`.
- maximum observed optimized-vs-reference state delta: `0` on tested cases.

### Run

```bash
node benchmark.mjs
```

All sibling `*.mjs` files are standard ESM; require Node 20+ for `structuredClone` and built-in `node:crypto`.

### Next release: v0.5

Introduce a durable, signed checkpoint boundary and external witness replay, with separate-process reference verification and named failure/recovery transitions. **No claim of production or physical quantum readiness yet.**