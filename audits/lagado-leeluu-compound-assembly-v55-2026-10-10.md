# Lagado / LEELUU v55 — Chemistry Projection of Seven Frozen Glyph Positions
Date: 2026-10-10
Parent: audits/lagado-leeluu-element-based-palette-v54-1-2026-10-10.md
Status: COMPUTATIONAL COMPOUND HYPOTHESIS / RDKit VALENCE PASS / HISTORICAL SOURCE CLOSED AND UNALTERED

## Frozen model vs new projection
Frozen original 16×16 engraving model and all 256 glyph positions, the user-set 200 atom-role +54 operants + 2 P1/P16 witness ontology, the earlier **109 selected similarity-MODEL bonds**, and the **11 separately designated candidate adjacencies** are completely unchanged. Neither similarity-selected edge nor proposed adjacency is established as a real chemical bond.

User supplied the element-based color reinterpretation:
- Green oxygen-based: K8 and L9 (O x2)
- Orange hydrogen-based: L8, M8, N8 (H x3)
- Blue nitrogen-based: N9 (N x1)
- Purple neon-based: M9 (Ne x1).
Only these seven glyphs were selected from the Test054 stable pair K8-L8 and the connected square and pair L8-L9, M8,N8,M9,N9. The original 8 color classes were never retrained.

## Best single connected conventional-valence candidate
The six non-neon atom interpretations match the molecular composition **H3NO2**. The database-listed formula / SMILES is **aminohydroperoxide, H2N–O–O–H (SMILES NOO)**, PubChem CID 17994906. PubChem: https://pubchem.ncbi.nlm.nih.gov/compound/Aminohydroperoxide
Formal chemical assembly assigned source glyphs:
- N9 N bonded to M8 H, N8 H and L9 O;
- L9 O bonded to N9 N and K8 O;
- K8 O bonded to L9 O and L8 H;
- M9 Ne remains **COMPLETELY UNBONDED** (spectator, not added to a single covalent molecule).
All FIVE chemical bonds are single; valence sum N 3, O 2 each, H 1 each, Ne 0. RDKit 2025.09.4 sanitization/explicit H/formula **H3NO2** and MMFF94 3D conformer optimization converged. RDKit predicted molecular weight 49.029 g/mol for the six-atom molecule. Atomic source composition including spectator Ne is H3NO2 + Ne; DO NOT misrepresent this mixture as a bonded molecule containing Ne.

Only TWO source pairs overlap with hypothesized chemical bonds:
1. K8–L8 is an existing proposed dormant grid-neighbor pair, but not accepted among the 109 similarity-MODEL links.
2. N8–N9 was an original accepted similarity-MODEL bond, still NOT an empirically identified chemical bond.
Other molecular chemical edges were intentionally added based on ordinary valence assumptions, not taken from original engraved adjacency or decoded material chemistry. The valence-valid identity is one possible chemistry reading under arbitrarily assigned atom types, not source-decoding or evidence of stable synthetic material. The catalog entry does not verify aminohydroperoxide is stable/isolable.

## Conservative alternative
Same inventory may be partitioned into separate established chemical species **nitrous acid HONO (HNO2) + dihydrogen H2 + neon Ne**. NIST Chemistry WebBook independently documents nitrous acid: https://webbook.nist.gov/cgi/cbook.cgi?ID=C7782776&Mask=58
That alternative is a mixture, not one covalent species or a proposed reaction product. Ne as a separate inert matrix is a meaningful chemistry analogy but has NOT been identified physically in the source photograph (neon-matrix example: https://academic.oup.com/mnras/article/419/2/1713/989620).

## Reproducible build / delivery
- Fully offline interactive 3D ball-and-stick viewer `LEELUU_compound_v55_lab.html`, color-keyed by assigned element and with address labels K8/L8/L9/M8/N8/M9/N9, rotation slider and auto-spin, element/valence summary, source link vs chemistry link selector and separate HONO+H2+Ne view.
- RDKit source builder `build_leeluu_compound_v55.py`, browser regression `test_leeluu_compound_v55_browser.py`.
- Actual 3D structure `LEELUU_aminohydroperoxide_H3NO2.sdf`, separate comparator `LEELUU_alt_nitrous_acid_HNO2.sdf`, `LEELUU_alt_hydrogen_H2.sdf`, source-mapped seven-atom visualization `LEELUU_seven_atoms_Ne_spectator.xyz` (with M9 Ne unbonded), mapping and source-vs-chemistry CSVs, detailed Markdown report and JSON summary.
- Rechecked against original frozen v41 role and v45 color CSV for all seven glyphs. Frozen v53 motif table also packaged for traceability.
- Chromium Playwright **17 / 17 browser checks PASS**, zero JS errors. Clean-room unpack and regenerate **6 / 6** tracked derived assets byte-for-byte. Build twice generates identical ZIP bytes.
- Bundle `LEELUU_compound_v55_bundle.zip`, **16 members**, SHA256 **93cd169682dce44333fc35d0e6497d9e48e77e07b90c8fb64d7838cbb380ff9a**, per-file SHA256 manifest and ZIP CRC verified. Complete offline HTML preview screenshot included.
- No previous frozen archive, source image, role table, original selected bond, candidate link or past audit overwritten.

DECISION: VALENCE-CORRECT COMPUTED ONE-MOLECULE CANDIDATE WITH NE SPECTATOR. NO SOURCE-VALIDATED CHEMICAL ELEMENT OR COMPOUND IDENTIFICATION. Preserve experimental limits and v54 immutable prior evidence.
