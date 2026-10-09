# Lagado Test 006 — Append-only molecular lineage / witness
DATE::2026-10-09
STATUS::PASS_ENGINEERING_INVARIANTS::NO_DECIPHERMENT_CLAIM
LINKAGE::audits/lagado-molecular-reactions-v5-2026-10-09.md
SOURCE::lagado_atomic_v3_atoms.csv
MODEL::{{1|1|2|4|8}}^{{n}}
GEOMETRY::256_SITES_16x16::480_LOCAL_NEIGHBOR_EDGES
GEN::GEN0_TO_GEN4
INPUT::53_V5_ACCEPTED_SWAPS::EXACT_SAME_SEQUENCE
IDENTITY::256_UNIQUE_SHELL_TOKEN_IDS_ASSIGNED_AT_GEN0
CORE::FIXED_PER_SITE
SHELL::MOVABLE_TOKEN::8_BIT_VALUE
LEDGER::APPEND_ONLY::SHA256_PREVIOUS_AND_ENTRY_LINKS

## Observed continuity
- All 53 original v5 swaps replayed; exactly 97 distinct shells moved at least once, 106 total token-hops, max 2 per identity.
- Source 256 shells contained 102 distinct 8-bit shell patterns; 49 repeated shell values; 774 identical-value pairs. Consequently a final unlabeled shell image cannot uniquely identify shell origins.
- Reverse replay exactly restored both shell **values** and all 256 assigned shell **identities** to their Gen0 positions.
- Core occupied bits 1166, shell occupied bits 1024, total 2190 invariant under swaps.
- Full chain verified relative to an initial anchor and terminal digest; 53/53 deleted-event and 53/53 one-field mutation tests rejected, 52/52 neighboring-event reorderings rejected.
- All 52 adjacent reorderings still yielded the same final **unlabeled geometry** under pure swap semantics, illustrating why endpoint geometry does not determine ordered history.
- A SHA-256 hash chain is tamper-evident only **with a trusted independently preserved anchor/tip**; a writer can recompute the chain if both digest and history may be replaced. No authenticated historical provenance is claimed.

## Gen0–Gen4 molecule membership
| Generation | Bonds | Components | Largest | Merge events | Split events | Shells moved |
|---|---:|---:|---:|---:|---:|---:|
| Gen0 | 64 | 195 | 10 | 0 | 0 | 0 |
| Gen1 | 100 | 160 | 17 | 20 | 0 | 56 |
| Gen2 | 110 | 150 | 17 | 8 | 0 | 70 |
| Gen3 | 120 | 140 | 21 | 9 | 1 | 85 |
| Gen4 | 129 | 133 | 22 | 7 | 1 | 97 |

Largest Gen4 group: 22 sites with nine Gen0 site-component ancestors; seven current sites hold shell tokens that originated outside the 22-site group. Component genealogies are based on site overlap in the bond graph; they are not hereditary biological ancestry.

## Test declaration
PASS::EXACT_VALUE_RECONSTRUCTION
PASS::EXACT_IDENTITY_RECONSTRUCTION
PASS::LOCAL_EVENT_BOND_RECALCULATION
PASS::SHELL_MULTISET_CONSERVATION
PASS::HASH_LINK_INTEGRITY_WITH_ANCHOR
PASS::MISSING_MODIFIED_REORDERED_EVENT_DETECTION
NOT_TESTED::NEW_INDEPENDENT_ENGRAVING_EDITION
NOT_PROVEN::ALCHEMICAL_OR_ATOMIC_HISTORIC_CIPHER
NOT_PROVEN::EXTRA_DIMENSIONS_OR_PHYSICAL_TIME_DILATION

## Interpretation
This tests an engineered deterministic transaction history on **image-derived symbolic bits**, not matter, genes, or actual chemistry. The same reaction optimizer and bias from v5 apply; localized spatial style remains a plausible source of apparent clustering. Next falsification is blind extraction on an independent scan, perturbing crop and binarization; compare against intact 4x4 block- and column-preserving controls.

ARTIFACTS::lagado_molecular_lineage_v6_bundle.zip::source_python+data+hashes+ledgers+HTML+report
