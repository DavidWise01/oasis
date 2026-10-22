# {{i}} chemical cipher — nested zipper invariant

Interpretation: Neon occupies 10 ordered address/value cells; Argon extends by eight independently addressed cells. Their crossed traversal interleaves the original Neon cells with the Argon extension in reverse order. A decoder checks the crossing and reconstructs the canonical core + extension.

**Invariant**: decode(encode(C10,E8)) = C10 || E8, preserving addresses 1..18 and byte values. The crossing order is derived; no irreversible edits or physical chemistry claims.

## Verification

Run `python3 docs/y2038/step_cipher_nested.py`. On the local environment, 10,000 deterministic randomized records passed bit-exact round trips and 5 malformed nesting mutations were rejected.

A nested pair/brace grammar beyond this defined zipper permutation has **not** been shown to be unambiguously reversible. This is a valid proposed symbolic encoding, not evidence of novel atomic behavior. No production infrastructure is required.
