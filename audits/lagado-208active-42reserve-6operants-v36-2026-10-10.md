# Lagado Test036 — Canonical Operant/Reserve Capacity Correction
Date: 2026-10-10
Parent: audits/lagado-archival-partial-replication-ascii-v35-2026-10-10.md
STATE::USER_CORRECTED::208_ACTIVE::42_RESERVE::6_OPERANTS

## Arithmetic and semantics
The prior v35 figure "208 active + 48 reserve" was a conflation. Correct partition of the 16x16 / 256-cell original source is:

```
256 SOURCE SLOTS
  ├── 208 ACTIVE ATOMS (unchanged; P16 is the preexisting witness within the grid)
  ├──  42 PASSIVE RESERVE SLOTS
  └──   6 OPERANT SLOTS
          ├── - + -
          └── + - +
```

Invariants: 208+42+6=256; 42+6=48. The canonical six-operant string is `-+- +-+` (two three-position groups, not six additional locations outside the original grid).
All 208 active site identifiers, 382 original grid-neighbor links, 109 frozen symbolic geometric bonds, 7 first-scan ink loop sites, and prior v35 second-photograph partial comparison are unchanged. Historical v35 artifacts remain append-only.

## Open mapping and evidence distinction
The original v22 graph enumerates all 208 active addresses. The complement contains 48 nonactive source coordinates, and we now regard this complement as a 42+6 **logical partition**.
**Which six of the 48 printed source addresses are operants has NOT been specified or independently identified in the engravings.** Accordingly the new ASCII atlas and v36 machine-readable schema do *not* invent operant address membership. All 48 candidate addresses are retained as an unallocated pool and there are six explicit numbered operant ports. Once a placement rule is supplied, those six coordinates can be assigned from the existing 48 without touching active ids.

This corrects an accounting / ontology error; it is not evidence of genomic, neural, temporal, or historical reading semantics. The second photograph still covers only A-E, with 56 active measured source cells; seven stable hole anchors lie below the crop.

## Corrected v36 local release
- lagado_full_ascii_v36.txt — 124-line comprehensive pure ASCII kernel atlas, corrected partition and the same existing active address map and graph pipeline
- lagado_capacity_v36.json — counts, 208 frozen active IDs, 48 eligible nonactive IDs, six ordered **unallocated** ports, witness and unchanged-original flags
- lagado_capacity_v36_report.md — correction and limitations
- lagado_capacity_correction_v36.zip — these three files, v35 original ASCII state and frozen v22 nodes/edges, SHA-256 manifest. All archive bytes and count checks pass.
- ZIP SHA-256: 81326a54ef78b3639a7435d102dc3037ba545c6baac812439fe619f3d6b3175b
- Excluded retired EE annotation absent from all newly derived text.
Audit state: APPEND_ONLY / CAPACITY_CORRECTION / SIX_OPERANT_ADDRESSES_UNALLOCATED.