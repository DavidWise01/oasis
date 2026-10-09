# Lagado Atomic Foundry — Test 011 (2026-10-09)

STATUS: ENGINEERING PASS / CHEMICAL REFERENCE PRESETS / HISTORICAL DECIPHERMENT UNPROVEN

LINEAGE: audits/lagado-vector-fractal-v10-2026-10-09.md

## Two consciously independent layers
1. **Real atom reference presets:** 10 neutral atoms H→Ne, each with Z protons, Z electrons, and a stated selected isotope neutron count A−Z. Electron configurations use occupied 1s, 2s and 2p orbitals; simple shell circles are educational diagrams and not orbital dynamics. Neon-20: 10 protons, 10 neutrons, 10 electrons; 1s² 2s² 2p⁶; shells [2,8].
2. **Image-derived symbolic atoms:** 256 sources from an approximate Academy of Lagado engraving, including 4×4 binary occupancy codes, 41×41 skeleton-reduced straight vectors, signed 9/6/3/1 signature, original core/shell 8+8 bits, and exact 36-digit virtual addresses. They are NOT identified as real chemical elements.

## Verified source regeneration and counts
- 256 glyph codes regenerated exactly from the v10 source image and matched input.
- 238 distinct source codes; 213 distinct dihedral D4 orientation classes.
- 3,102 traced straight-vector segments.
- Original Gen0 spatial vector-neighbor gate, 480 possible grid edges: 64 relaxed and 13 strict candidate edges. This reuses the v10 nine-bin soft descriptor and axis criterion.
- Relaxed pair gate: 3×3 soft descriptor cosine ≥0.90; orientation L2 ≤0.65.
- Strict pair gate: cosine ≥0.95; orientation L2 ≤0.50.
- 256/256 unique D4 orientation reversibility checks pass for rotation/mirror; 256/256 virtual 36-digit regenerations pass; 10/10 real reference electron counts/neutrality pass.
- Browser Chromium Playwright executes the self-contained HTML: select Ne, select A1, rotate 90° and forge derived child with retained Gen0 origin; in-browser validation prints 11/11 PASS and no JS runtime errors.
- ZIP integrity passes; JS syntax passes `node --check`.

## Nested registers
9 = signed overlapping 2×2 window occupancy of *unmodified Gen0* 4×4 glyph; 6 = signed row/column sums; 3 = [4-neighbor left→right path, cycle, top→bottom path]; 1 = sign of total signed nine sum. This differs from v8, whose source mapping used an already-mutated Gen4 shell.
The 36-step `9|6|3|1` address is a virtual base-10 nested address and does not imply a physical 10^-36 m measurement. It introduces no information beyond the source 16-bit symbol.

## Interactive implementation
An offline, dependency-free HTML builder provides 10 chemistry preset selectors, 256-cell glyph selector, source path drawing, live signed register inspector, virtual depth 1–36, D4 child rotation/mirroring with append-only in-session event ledger, adjacent-cell geometric bond bench, JSON export, and validation tests. Each child is a geometric transformation of a single Gen0 source, never fabricated source evidence.

## Sources and outcome limitations
The v10 source image is extraction-sensitive, as established in v9. The v10 original vector graph did not beat intact 4×4-block spatial controls: relaxed p≈0.125; strict p≈0.514. This is a working **symbolic atom construction tool**, not proof of a historical alchemical key, deciphered language, chemistry, or Planck-scale dynamics.

## Exact local artifact digests
- `lagado_atom_foundry_v11.html` SHA256 `4cca1f54978adeaeec4ec85f9868f5da5c2d427b46c80c183a15a5f703987ac6`
- `lagado_atom_foundry_v11.json` SHA256 `a0ecca4a46372c2bdced1e0932281a8e9ff2f39027185980182b637a36cdee9b`
- `lagado_atom_foundry_v11_bundle.zip` SHA256 `9289619658759be7e805963bd4b4122d8fe7fd0943d7d71a9cdf5b399ccc3703`

Next target: physically grounded valence/reference examples in a distinct chemical layer; and independently rectified historical engraving re-extraction for the symbolic bond layer.
