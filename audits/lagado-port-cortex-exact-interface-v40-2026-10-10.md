# Lagado Test040 — Exact Minimum Port-to-Cortex Interface
DATE::2026-10-10
STATUS::ENGINEERING_PASS::SOURCE_BONDS_FROZEN::11_VIRTUAL_GATE_OVERLAY::NO_HISTORICAL_DECODING
PARENT::audits/lagado-six-operant-routing-test-v39-2026-10-10.md

## Frozen source and strict partition
The frozen original engraving representation is 16x16 source slots = 208 active + 42 reserve + 6 provisional signed operant slots, six signs `-+- +-+`. P16 remains the original witness, not a new extra slot.
Original Test022 graph is 208 nodes, 109 accepted **model-defined** geometry bonds and 382 source-grid adjacencies. 273 grid adjacencies are NOT accepted original model bonds. Test024 12-channel cortex state and Test037 operant positions remain unchanged: left A5(-), C2(+), L1(-), right A12(+), C15(-), L16(+).
No original bond, symbol, cell address, legacy file or source image was overwritten or inferred to be an actual historical circuit.

## Problem and EXACT combinatorial answer
A5 has original grid contact atoms A6 and B5; C2 has C3 and D2; L1 has L2 and K1. These six atoms occupy six mutually distinct original 109-bond connected components, none connected to the existing A7-A8-A9-A10 cross-hemisphere bridge component. Including A7, there are exactly SEVEN terminal components among 101 original bond components.
Only allow enabling a link if it is ALREADY a grid adjacency among the 382 but NOT among original 109 bonds. A new virtual gate has cost exactly 1; existing original bonds have cost 0. Target: connect ALL six port contacts to original A7 component using the fewest enabled virtual links, with no long-distance invented edges.
We solved an exact Dreyfus-Wagner subset dynamic-programming Steiner tree problem on the quotient graph obtained by collapsing all 101 original-bond components. EXACT MINIMUM = **11 virtual gates**. For each required pair of quotient components, resolve multiple equivalent original cell-to-cell adjacencies by deterministic source-address lexicographic ordering, NOT by optimizing observed signal gain.

Eleven selected exact source-grid adjacencies:
```
G01 A6--A7    G02 A7--B7    G03 B4--B5
G04 C3--C4    G05 C4--D4    G06 B5--B6
G07 D4--E4    G08 E4--F4    G09 F4--G4
G10 H3--I3    G11 K1--K2
```
These 11 are **added virtual routing gates**, explicitly distinct from unchanged source bonds. The combined simulated traversable overlay has 120 links: 109 original + 11 new virtual. All 11 are individually critical to retaining connectivity from ALL six contacts to A7; removing any one fails the all-six requirement. This is an engineered fault-tolerance defect, not physical evidence.

## Three routing configurations
Frozen (0 added): no left port has a path to the right; all right-side signal mass zero.
Single-gate (A6--A7): half of A5's injected activity can access the previously existing 18-node A7 component, while C2 and L1 remain disconnected.
All-11: all six contacts are graph-reachable to A7; shortest route into right region A5=4 hops, C2=9 hops, L1=19 hops. Signal mass still split among many branches.

Conservative lazy random walk: at each tick hold 0.5 locally, distribute 0.5 among traversable neighbors with normalized weights. Uniform W=1; cortex W=2^(-abs(g_i-g_j)); signed W=cortex*2^(phase_t*(col_j-col_i)), six phases `-+-+-+`. These are CHOSEN simulator rules; time step is not physical time.
Right-region activity at t48 with signed controller:
- Frozen: A5=0, C2=0, L1=0.
- One gate A6--A7: A5=22.492752%, C2=0, L1=0.
- All 11 gates: A5=12.926305%, C2=0.810296%, L1=0.000173%.
At tick96 with all 11: A5=18.761254%, C2=3.305911%, L1=0.025483%.
Original bonds and total probability mass conserved. Adding more routes can reduce *right-side* mass at a finite tick by diffusion into other branches, so more connectivity is not monotonically more throughput.

## Exact controls and limitations
Preexisting 12 equally contact-rich v37 geometric operant-location layouts tested against identical exact minimum gate objective. Minimum counts: [11,12,13,11,12,13,10,11,12,11,12,13]. User's currently assigned layout costs 11; another alternative 10. No special geometric optimality for the chosen placement.
All 20 six-place balanced sign schedules with exactly 3 plus and 3 minus were compared on frozen complete 11-gate topology; prescribed `-+-+-+` ranks t48 right-mass 12/20 for A5, 10/20 for C2, 10/20 for L1. No preferential encoding of this order established.
Gates were *designed* to satisfy connectivity; resulting successful reachability is not statistical evidence of historical hidden code, DNA, time physics, or biological brain wiring.
Preexisting original A7 bonded component was scan-extraction-sensitive in Test019 and the lower 7 ink-loop source positions remain unverified on the incomplete historical second-photo crop.

## Artifacts, tests and integrity
Generated: `build_lagado_interface_v40.py` (full standalone exact subset DP + simulation), `build_lagado_interface_v40_ui.py`, `test_lagado_interface_v40_browser.py`, `write_lagado_interface_v40_docs.py`, original frozen v22/v24/v37 CSVs, exact 11 gate map CSV, 3 configurations x 4 seeds x 3 routing policies x 97 tick trace CSV, t12/t24/t48/t96 score CSV, all 20 balanced phase results per three left ports, all 12 alternative exact gates CSV, JSON result, full ASCII atlas, Markdown report, embedded-data interactive SVG lab and screenshot, SHA256 manifest.
Chromium Playwright **16/16 checks PASS**: original 109 lines, 11 gates, 256 slots, select seeds, 0/1/11 gates, conservation, t48/t96 patterns, phase ranking, source inspection, reset/step actions and zero JS errors. Deterministic ZIP 21 files, ZIP CRC PASS, per member SHA256 PASS, repeat ZIP byte hash same in two builds. ZIP SHA256 **cca03678fe0c2519a48e2cf191eb690dbb84d17f9d70d0690e2e02e41d9912e0**. New derived text files exclude the retired annotation.

NEXT::TEST041_MINIMAL_SINGLE_GATE_FAILURE_TOLERANCE::explicitly find redundant original-grid gate overlay satisfying full left-contact-to-cortex reachability after any one virtual gate fails; report added gate count, non-recoverable components and sensitivity before building an optimized controller.
AUDIT::APPEND_ONLY::ENGINEERING_VALIDATION_NOT_SOURCE_DECODING
