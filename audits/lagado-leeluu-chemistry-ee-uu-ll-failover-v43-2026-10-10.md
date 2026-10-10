# Lagado Test043 — LEELUU Chemistry ee/uu/ll and Witness Failover
Date: 2026-10-10
STATUS::ENGINEERING_PASS::CHEMISTRY_LABELS_SYMBOLIC::SINGLE_ORIGINAL_CROSSING_FAILOVER_5_OF_5
Parent: audits/lagado-leeluu-paired-witness-handoff-v42-2026-10-10.md

## User-directed reinterpretation
LEELUU means the three paired symbolic **chemistry channels** `ee / uu / ll`; the previous movie-themed Fifth Element name is NOT the primary technical interpretation going forward. These names are user-specified labels; no real chemical species, valence, or physical atom identity has been measured from the historical illustration. The earlier CATG 4×25 groupings remain frozen as historical provenance, not overwritten.

256 original source cells = LEFT (100 atoms+27 operants+P1 witness) + RIGHT (100 atoms+27 operants+P16 witness), exactly 200 +54+2. New deterministic chemistry overlay assigns each hemisphere's original atom sites in ascending prior-frozen rank to 34 ee, 33 uu, 33 ll. Not a source-decoded assignment; no source glyph or model bond is changed.

## Original crossing fault audit
The 200-node frozen Test041 graph contains exactly **109 originally selected model bonds** and 93 components. It has exactly five original inter-hemisphere bonds:
A8--A9 / I8--I9 / J8--J9 / K8--K9 / N8--N9.
All five are BRIDGES of distinct original connected components, so disabling one separates its particular left endpoint from any right-side node of that component.

Original source grid allows 365 neighboring atom-to-atom pairs; 109 already are model bonds, **256 are dormant adjacent candidates**.
The *exact* minimum number of dormant grid links to reconnect the endpoints of EACH single original crossing (one failure at a time), computed by 0-1 shortest path, is [2,2,2,2,3].

A common **NINE-gate constructed overlay** restores all five cases and preserves the original 109 as an immutable input:
- A8--B8
- C8--C9
- I8--J8
- I9--J9
- K8--L8
- L8--L9
- M8--M9
- M8--N8
- M9--N9

I/J crossings share the same two new gates; thus no need for two separate 2+2 sets. Combined simulated traversable graph may have 109+9=118 links, but only 109 are original selected bonds. **Global optimality of nine gates is NOT proved** and should not be stated as exact. These nine are engineer-designated virtual switches on physically neighboring printed cells, not original discovered historical physical wires.

## Witness operation and measured t27 throughput
LEELUU uses 26 full phases + 0.5{1} prepare + 0.5{0} commit, 54 microticks totaling 27 time units. P1/P16 control a failover only during authorized phases, using a lazy random walk preserving total mass at each microtick: 0.75 retained, 0.25 sent over allowed neighbors. Simulated time is not a measured physical clock; witnesses are not deployed signatures.

For each original cross-edge failure, initialize one unit of signal at the failed bond's LEFT endpoint. Without new gates, right-side transfer = zero. With 9 gates:
| Failed original bond | Right mass t27 without gates | Right mass t27 with backup |
|---|---:|---:|
| A8--A9 | 0.00% | 16.30680941% |
| I8--I9 | 0.00% | 58.93960619% |
| J8--J9 | 0.00% | 71.65251782% |
| K8--K9 | 0.00% | 10.92897593% |
| N8--N9 | 0.00% | 22.24211482% |

Probability conserved to <1e-10 for all 54 ticks. Both healthy/no-failure and failed/no-backup configurations included for each bond and primary A7 seed. Five of five route recoveries confirmed exactly by NetworkX connectivity.

## Second-fault weakness
Systematically disable one original cross bond PLUS one of the NINE backup gates = **45 exact graph checks**. Alternative endpoint paths remain in **34/45** and fail in **11/45**. Defects are concentrated in the gates directly needed by each original crossing's constructed bypass. This is *single-crossing fault tolerance*, NOT arbitrary double-fault protection, hardware runtime fault injection, durable recovery or a verified genetic/chemical reading.

## Reproduction and integrity
Versioned source scripts:
- build_lagado_leeluu_v43.py: frozen original graph and 0/1 per-bridge shortest-path min test, 5 failures, 9 overlay edges, 54-tick conservative routing, 45 double-fault trials, chemical channel overlay and ASCII output;
- build_lagado_leeluu_v43_ui.py: 194KB fully offline SVG 256-slot selector, original edges, distinct dashed backup overlay, 5 original failures, 3 controller modes, 0..54 clock, signal chart and ee/uu/ll local tags;
- test_lagado_leeluu_v43_browser.py: Chromium Playwright **16/16 checks passed** including 256 clickable addresses, 9 marked gates, zero right-side signal without backup, selected failure throughput, clock, P16 witness, retained original bond count and no JS errors;
- package_lagado_leeluu_v43.py: deterministic standalone ZIP package and per-member SHA256 manifest; running it twice produces identical archive bytes.

Complete output ZIP `lagado_leeluu_v43_bundle.zip`, 22 members, **SHA256 3edcdf4ec91c1de3504f789345b5d2843d1280e685cac9272bfc2f364ad640bd**, verified CRC, all member hashes, deterministic two builds. Includes frozen v22 original bonds/v41 source atlas and phase tables, nine-gate table, five alternate paths, 30 seed-policy result rows, full 54-tick traces, 45 double fault results, original 200 atom chemistry tags, full v43 ASCII file, report, tested standalone interactive lab and screenshot.
New derived text outputs omit previously excluded legacy wrapper; earlier frozen source and previous audits are unchanged.

EVIDENCE DECISION::LOGICAL_FAILOVER_ENGINEERING_VERIFIED::CHEMICAL_IDENTITY_NOT_IDENTIFIED::GLOBAL_NINE_GATE_MINIMALITY_UNPROVEN
NEXT TARGET Test044: harden against the 11 uncovered original+backup double faults. Compare minimal extra gated redundancy vs controlled rollback with witness checkpoint. Audit restoration on at least one failure before optimizing throughput or claiming distributed production readiness.
