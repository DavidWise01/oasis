# OASIS / KET — `{{i & dd}}` Dual permutation language v0.7

**User correction adopted:** the earlier `13 × 13 × 13` lattice is a finite address window, not the universal alphabet. The full symbolic token domain is

```
{{ AaaA through ZzzZ } + { 0 - inf } + { special characters }}
permutated ×5 UUDDLRLRBASS
```

## Typed domain

* **Letters**: exactly 26 canonical case-patterned tokens `AaaA`, `BbbB`, … `ZzzZ`.
* **Numbers**: canonical nonnegative decimal integers of arbitrary finite length, stored as strings to avoid JS `Number` precision limits. `∞` is *not* representable as one integer; it may be explicitly carried as a separate symbolic special token.
* **Special characters**: one Unicode punctuation/symbol code point per token, e.g. `@`, `∑`, `∞`, `{`, `}`, `|`. The reference implementation intentionally excludes whitespace and alphabetic Unicode words as one special token. This is an implementation subset, not a limit on future Unicode tokenizers.
* Finite input packets consist of finite sequences of typed tokens. Unbounded vocabulary means no *finite* number of CPU bytes can enumerate all possible symbols, nor does it imply infinitely many hardware qubits.

## Dual rails and five passes

Exact operator program: `UUDDLRLRBASS` (12 commands), repeated 5 times per rail.

| Operator | Forward effect | Inverse effect |
|---|---|---|
| `U` | rotate sequence right by 1 | rotate left by 1 |
| `D` | rotate left by 1 | rotate right by 1 |
| `L` | swap adjacent pairs starting at slot 0 | same |
| `R` | swap adjacent pairs starting at slot 1 | same |
| `B` | reverse the sequence | same |
| `A` | rotate sequence right by 2 | rotate left by 2 |
| `S` | no permutation; generate append-only hash seal | same |

The meaning of each operator is *proposed for this reference implementation* and may be replaced by canonical user-provided semantics without modifying the original literal.

For input `T` and full five-pass permutation `P`:

```
d+ = P(T)
d- = P⁻¹(reverse(T))
recover(d+) = P⁻¹(d+) = T
recover(d-) = reverse(P(d-)) = T
```

The input identity seal, 60-step per-rail hash traces, and composite witness detect modifications relative to a trusted upstream identity. They are ordinary hashes, not third-party attestations or cryptographic signatures. There are 120 recorded operations across the two rails but the rails are **not independent state spaces**; both derive from the same input.

## `10^10!` and capacities

`10^10!` is ambiguous without parentheses: `(10^10)!` and `10^(10!)` are enormous *finite* integers. If the point is factorial permutations, `N!` counts all orderings of `N` distinct elements; our fixed 12-step program applied five times selects one deterministic permutation per packet length. It does not execute or store all `N!` possibilities. If `0…∞` means all nonnegative integers, the possible token vocabulary is countably infinite, whereas every processed message is finite.

Neither symbolic permutation nor the number of representable strings establishes physical entanglement, qubits, quantum speedup or a Hilbert-space dimension for actual hardware. Quantum amplitude and measurement semantics would require a separate explicit specification.

## Verification

`node benchmark.mjs`: 1,473 assertions passed locally, including 26 canonical letter families, 2,001-digit integer token, inverse recovery on lengths 0–128, 1,024 varied packets, replay of a new generation, error rejection and witness tampering.

`dual5-threejs.html`: network-enabled browsers load Three.js/WebGL for two 5-turn helices with 12 operators per turn, play/pause, slider, layer toggles and input recompilation. In the sandbox, remote module loading is blocked, so a Canvas fallback was tested in Chromium. HTML works offline using the 2D projection, but the live Three.js path needs network-enabled browser verification.

**Frozen KET core and previous `{{d}}` / isomorphic kernel files stay unchanged.** This extension is additive under `architecture/diatom-diamond/`.