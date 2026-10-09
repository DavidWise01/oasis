# Lagado Cipher — Test 005: Symbolic Molecular Reactions

DATE::2026-10-09
STATUS::EXPLORATORY_SIMULATION::NOT_HISTORICAL_DECIPHERMENT
LINEAGE::audits/lagado-molecular-nesting-v4-2026-10-09.md
SOURCE::SOTHEBYS_LAGADO_1726_ENGRAVING_APPROXIMATE_BINARIZED_GRID
SOURCE_INPUT::lagado_atomic_v3_atoms.csv

## Experiment
256 approximated 16-bit glyphs in 16 × 16 arrangement, interpreted as symbolic atoms.
NEST::{{1|1|2|4|8}}^{{n}}
CORE::FIRST_8_BITS
SHELL::LAST_8_BITS
BOND::NEIGHBOR_ADJACENCY_AND_CORE_HAMMING_LE_2_AND_SHELL_HAMMING_LE_2
REACTION::EXCHANGE_ENTIRE_8_BIT_SHELLS_BETWEEN_ADJACENT_SITES_IF_AND_ONLY_IF_LOCAL_NET_BOND_GAIN_GT_0
GEN0::BASELINE
GEN1::HORIZONTAL_EVEN_PAIRING
GEN2::VERTICAL_EVEN_PAIRING
GEN3::HORIZONTAL_ODD_PAIRING
GEN4::VERTICAL_ODD_PAIRING
STAGES::APPEND_ONLY_LEDGER
CONTROL::4_NULL_MODELS_RUN_SAME_OPTIMIZATION

## Results
| Gen | Qualifying bonds | Accepted swaps | Bonds formed | Bonds broken | Largest molecule |
|---|---:|---:|---:|---:|---:|
| Gen0 | 64 | 0 | 0 | 0 | 10 |
| Gen1 | 100 | 28 | 37 | 1 | 17 |
| Gen2 | 110 | 9 | 10 | 0 | 17 |
| Gen3 | 120 | 8 | 12 | 2 | 21 |
| Gen4 | 129 | 8 | 10 | 1 | 22 |

- Total swaps accepted: 53 of 480 candidate neighboring pair proposals across four generations.
- Core occupied bits conserved: 1166.
- Shell occupied bits conserved: 1024.
- Total occupied bits conserved: 2190.
- Full multiset of 8-bit shell states conserved exactly.
- Reverse application of all 53 event records restored the original state exactly (test PASS).
- Normalized vessel occupancy H=1.000 throughout; this is guaranteed by the definition of the operator, *not* evidence that physical biological homeostasis has been demonstrated.
- Component splits across Gen1–4: 0, 0, 1, 1; component joins: 20, 8, 9, 7.

## 1200 equally optimized permutations each
| Control | Expected final bonds | p(final ≥129) | Expected gain | p(gain ≥65) |
|---|---:|---:|---:|---:|
| fully_shuffled | 96.062 | 0.00083 | 50.176 | 0.01582 |
| whole_rows | 109.580 | 0.00083 | 56.712 | 0.06245 |
| whole_columns | 121.844 | 0.12906 | 56.840 | 0.09575 |
| intact_4x4_blocks | 124.385 | 0.15654 | 61.757 | 0.21898 |

## Interpretation and limits
The programmed shell-exchange rule intentionally rewards greater bond counts: increases are not independently surprising. The original layout exceeds unrestricted random controls, but is **not distinguishable from column or 4×4-block preserving controls at conventional 0.05 significance**. The result supports an executable geometric-transaction model with exact bookkeeping; it does not decipher the original historical marks, establish real molecular reactions, or show that alchemical content was hidden in Swift's fictional writing machine.

NEXT_PROOF_GATE::INDEPENDENT_EDITION_SCAN::BLIND_GEOMETRY_EXTRACTION::PREDECLARED_THRESHOLDS::BLOCK_AWARE_NULL
