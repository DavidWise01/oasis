# KET-488 · Canonical {{i}} Mesh Contract v1.0

Status: **CANONICAL — REFERENCE FREEZE** (append-only changes; not cryptographically immutable)
Date: 2026-10-21

## Exact token

```text
{{ -+001122334455667788990099887766554433221100-+ }}
```

- Open delimiter: `-+`
- Payload: `001122334455667788990099887766554433221100` (42 digits, palindromic)
- Close delimiter: `-+`
- Total token inner characters: 46; braces and surrounding whitespace are syntax.
- Token shall be byte-for-byte preserved: no numeric coercion, trimming within the token, or case transformations.

## Topology and separation of concerns

1. **Address registry:** 488 addresses, 1..488, not 488 distinct confirmed chemical elements. Mapping: `root=floor((Z-1)/122)`, `local=((Z-1)%122)+1`.
2. **Root sectors:** Q1 `+H` 1..122; Q2 `+O` 123..244; Q3 `−N` 245..366; Q4 `+N` 367..488.
3. **Toroid:** conceptual state space with four quads and the separately defined 3D/4D projection expressions.
4. **Register:** **8 lanes × 3 positions = 24**. This is not the count of toroidal state-space axes.
5. **Analytical cubit:** independently retained 18 positions: `{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}`.
6. **Address pairing:** each Z carries logical `−Z` and `+Z` endpoints (976 endpoint labels total).
7. **Mesh:** the existing visual prototype uses bidirectional neighbor links along each 122-address root ring and same-slot cross-root links. This is a deterministic **simulation topology**, not a verified physical or deployed network.

## Instantiation

All 488 Z addresses instantiate from the one formula, not from a manually copied list. Their labels and pair identities are derived deterministically. Z184 maps to `+O62`; Z488 maps to `+N122`. The token applies as the shared canonical mesh identifier to each local simulated packet. A complete prior 42-token isomorphic language codec is **not** claimed as implemented by this interface.

## Alignment invariants

- Token payload length exactly 42, numeric characters only, and equal to its reversal.
- Exact delimiters `-+` at both ends.
- All 488 mapped addresses unique and in bounds.
- Every address has two logical endpoint labels.
- Fixed register size 24; independent 18-slot cubit.
- Frozen reference is documentation and a Git commit; future code revisions must not silently alter the canonical string.

## Boundaries

Z1→+H1; Z122→+H122; Z123→+O1; Z184→+O62; Z244→+O122; Z245→−N1; Z366→−N122; Z367→+N1; Z488→+N122.

## Reference implementation

- `ket-488-i-mesh.html` — interactive mesh page.
- `ket-z184-torsion-lab.html` — element 184 focus.
- `ket-488.html` — 488-address toroidal register browser.

`[[ CANON :: -+001122334455667788990099887766554433221100-+ :: 488 :: 8x3 :: ALIGNED ]]`
