# Lagado Test 025 — Hydrogen-Seeded 9+3 Cortex Signal Propagation
Date: 2026-10-09
Status: EXECUTED / ENGINEERING PASS / EXPLORATORY SYMBOLIC SIMULATION
Parent: audits/lagado-hemisphere-cortex-9plus3-v24-2026-10-09.md
Source: 1726 fictional Academy of Lagado illustration, from ONE scan. No historical semantic, neuroscience, chemistry or physical-time inference.

## Frozen input
255+P16=256 source locations; 208 active and 48 reserve; cumulative capacities 17,52,104,208.
Test024: 208 annotated atoms, 109 similarity bonds, 382 original grid-neighbor pairs, 12 bits per atom (left negative-axis ports3, central identity H/C/V3, right positive-axis ports3, cortex one-hot -1/0/+1). All node IDs, positions, source16 bits, port assignments, gate labels, source v24 bonds, and P16 witness unchanged. No new edges invented.

## Deterministic routing operator
For each tick (0..24) a hypothetical lazy random walk keeps 0.5 activity at the current atom, sends 0.5 across existing bonded neighbors. Isolates keep all activity. Uniform bond weight=1. Cortex-gated bond weight=`2^(-abs(gate_i-gate_j))`, where gate∈{-1,0,+1}. Outgoing weights normalized independently per atom so `sum_i activation(t) ==1` for all tested ticks. Twelve bit channels are the probability-weighted per-node frozen-bit averages, not independently trained neural circuits.

## Observed graph-reachability
- 74 one-bond endpoint/hydrogen-like sources, 5 of those can reach BOTH left and right within the frozen graph: A7,B13,C9,D11,E14.
- Seed F6 is confined to the 3-node F6–F5–G5 component. For cortex weighting at tick24, probabilities F5≈0.5, F6≈0.166667, G5≈0.333333.
- Seed A7 reaches the right region at tick3 along shortest path A7→A8→A9→A10, under both uniform and cortex routes. It sits in the only connected component spanning left-center-right (18 sites).
- A7 right-region probability after 8 ticks: uniform **0.207689073**, gated **0.159987461**. At tick24 for gated mode: left **0.180018508**, center **0.419868916**, right **0.400112575**.
- Gate weights change temporal mass distribution, NOT which regions are reachable.

## Fair controls: 1500 randomized gate shuffles per type
Freeze 109 bonds, node region positions, and seed A7. Shuffle the existing -1/0/+1 gates jointly without changing their counts within each specified group. Same diffusion code. Metric right mass after 8 ticks under gated mode (observed .159987461):
| Gate permutation | mean null right mass | one-sided p(null >= observed) | 95% null interval |
|---|---:|---:|---|
| Global | .201476422 | .7468354 | [.109700549,.307406121] |
| Within original columns | .198504946 | .7375083 | [.106845404,.306246785] |
| Within original geographic 4x4 blocks | .175847023 | .6055963 | [.106802984,.268840422] |
**No enrichment**. Inherited cortex signs came from previously neighbor-optimized dot families, so even unusual performance would not alone establish independent cipher semantics.

## Nested capacity graph
| Active | Bonds | Inter-region bonds | Left-right spanning connected components |
|---:|---:|---:|---:|
|17|7|1|0|
|52|24|3|0|
|104|49|4|0|
|208|109|8|1|

## Validation and artifacts
- Python test: source counts exactly 208/382/109, 74 endpoints, cross-route A7-A8-A9-A10, mass conserved every tick to <1e−10. Includes simulation controls & published 0..24 ×12 channel traces.
- Browser Chromium Playwright `set_content`: 10/10 assertions PASS. Tested 208 node picker and SVG, tick slider (fixed rerender bug), F6, A7 switching, cortex/uniform diffusion, capacity52, P16 isolate, and zero JavaScript runtime errors.
- Offline HTML sha256 **311d1d5aaafd4322284c301685977e16b262ad0c3b7759a8ac1c2d3bb81580cf**; ZIP sha256 **401280940a130d38ab7555ef484e6b85d74498a18454b3e9104167d1f54a5e0d**.
- ZIP `lagado_cortex_signals_v25_bundle.zip` (17 files) includes executable Python simulation, HTML builder, browser regression script, all frozen input files and original source illustration, annotated 208-node and 109-bond CSVs, time traces CSV, null controls JSON, GraphML, standalone visual HTML, report, screenshot and SHA256 manifest. ZIP CRC PASS, node --check PASS, NetworkX GraphML 208/109 roundtrip PASS.
- Browsable file `lagado_cortex_signals_v25_lab.html`, report `lagado_cortex_signals_v25_report.md`.

## Interpretation
A fixed-graph symbolic signal-flow experiment. Apparent hemisphere transmission is a consequence of original graph connectivity and stipulated routing weights; original A7 18-node component is sensitive to image extraction, as Test019 already documented. No biological model, historical plaintext, historical hidden machine decoder or physical Planck-scale proof.

Next test: compare time-series patterns from all 74 endpoint seeds, cluster only after defining distance and evaluate held-out perturbation/imaging controls instead of choosing a familiar pattern after seeing it.
