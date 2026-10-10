# Lagado Test041 — LEELUU Fifth-Element Dual-Hemisphere Repartition
Date: 2026-10-10
Status: ENGINEERING PASS / CANONICAL SYMBOLIC REGROUP / NO DECIPHERMENT
Parent: audits/lagado-port-cortex-exact-interface-v40-2026-10-10.md

## Canonical new live 256-cell partition
- Per hemisphere: 100 atoms + 27 operants + 1 witness = 128. Two hemispheres 200 + 54 + 2 = 256 original 16x16 source addresses, no unused cells.
- Left columns 1..8, right columns 9..16; original published glyph locations unchanged.
- Each 100-atom hemisphere is grouped into four mnemonic families of 25 using original frozen atom radial rank: C/Earth, A/Air, T/Fire, G/Water. The Fifth Element or LEELUU witness completes the mnemonic, not a historic biological/chemical finding.
- Left paired witness P1 (formerly non-active); right paired witness P16 (already the preexisting pinned original witness).
- 27 operants per hemisphere comprise 26 full signed-phase slots and ONE closing operant with two half phases 0.5{1}+0.5{0}=1. That is exactly 27 source cell positions, not 28 or fractional physical cells. Phase-to-glyph assignment is conventional and fixed.
- Existing 6 v37 operant source positions retained and now used as first three phase ports on each side: LEFT -+- at A5,C2,L1; RIGHT +-+ at A12,C15,L16. Remaining phases assigned in source row-major order (within hemisphere); 27th phase is a single source cell split into two sequential time registers.

## Repartition method and provenance
Previous Test040 live ontology 208 atoms / 42 reserve / 6 operants is preserved as a historical snapshot and superseded for new *role classification*.
Original 208-model atom positions comprise exactly 104 in each 8-column hemisphere. Explicitly reclassify seven original bond-degree-zero cells to operants, F1 F16 M2 M15 O5 O12 P8, and P16 from original atom-isolate to right witness. Choose P1 as left witness, since it is the column mirror of P16 and was a non-active original address.
Thus left: 104 old atom cells - 4 reclassified = 100 atoms; 24 old nonactive - P1 + 4 reclassified = 27 operants; P1 witness.
Right: 104 old atom cells - P16 - 3 reclassified = 100 atoms; 24 old nonactive + 3 reclassified = 27 operants; P16 witness.
All 109 original v22 similarity-selected *model bonds* still connect retained atom sites because the eight reassigned former source nodes were isolated. The original 382 grid-neighbor records remain in the frozen evidence ledger; 365 join two atoms under the new role view. Atom-only graph has 200 nodes / 109 original bonds / 93 components / 62 isolated retained atoms / largest component 18. The earlier exact 11 virtual interface links are NOT original source bonds and were not incorporated into the evidence graph.

## ASCII structural overview
```
                    256 ORIGINAL SOURCE CELLS
                               |
                     +---------+---------+
                     |                   |
                 LEFT 128            RIGHT 128
                  100+27+1           100+27+1
                     |                   |
        C25 A25 T25 G25        C25 A25 T25 G25
         26 FULL PHASES          26 FULL PHASES
         0.5{1}+0.5{0}           0.5{1}+0.5{0}
             P1                    P16
                     \               /
                       LEELUU / FIFTH
                           CATG::0
```
The LEELUU/four-elements nomenclature and CATG are deliberately symbolic analogies. No 27-node Hamiltonian cycle exists in the currently extracted atom bond graph: its largest connected component has only 18 nodes. The 27 phase ring is a *controller schedule*, not a discovered circuit or physical time claim.

## Test status and deliverables
Build script `build_lagado_leeluu_v41.py` deterministically derives a full 256-address role atlas, 54-address operant/phase CSV, eight 25-atom groups, schema JSON, full ASCII kernel, and a standalone interactive HTML viewer from frozen v22 node/edge records and v37 port IDs. Explicit assertions verify all count/symmetry/role/port/bond invariants.
Chromium Playwright 14/14 tests PASS, tested 256/200/54/2 visual atlas, two witnesses, phase 2, filtered role views, zero JS exceptions. Deterministic 14-file ZIP SHA256 ffccda88aee023cb3692fa7173c76146a23c1f0ed72c6b751ba92e33e1bfd741; ZIP CRC and per-member SHA256 integrity PASS; two clean packings byte-identical. All new derived text files exclude previously retired annotation. Frozen input image and earlier audits remain untouched.

Artifacts in conversation: `lagado_full_ascii_v41.txt`, `lagado_leeluu_v41_lab.html`, `lagado_leeluu_v41_bundle.zip`, `lagado_leeluu_v41_schema.json`, `lagado_leeluu_v41_atlas.csv`, `lagado_leeluu_v41_operants.csv`, `lagado_leeluu_v41_element_groups.csv`, `lagado_leeluu_v41_report.md`.

## Recommended Test042
Validate a 27-phase *controller* operating the frozen 109-bond 200-atom graph: mirrored witness handoff, half-step closure, mass conservation and resilience to disabled phases; compare its performance to alternative schedules before adding more virtual interface gates. This is an engineering benchmark, not source decoding.
