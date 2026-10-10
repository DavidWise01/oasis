# Lagado Test032 — Independent Archive Scan Replication Runner
Date: 2026-10-10
State: SOURCE_LOCATED / LOCKED_EXTRACTOR_VERIFIED / INDEPENDENT_PIXEL_REPLICATION_PENDING
Parent: audits/lagado-stable-loop-vector-grammar-v31-2026-10-10.md

## Archival acquisition
A separately digitized original book was located at Universitätsbibliothek Paderborn: Jonathan Swift, Travels into several remote nations of the world, Vol. II, London: Benjamin Motte, 1726, digitized by the library in 2019. The specific Plate V, Part III, page 74 shows the 16x16 writing-machine engraving with the same visibly arranged glyphs as the frozen first source.
Bibliographic record https://digital.ub.uni-paderborn.de/ihd/content/titleinfo/3081557
Plate https://digital.ub.uni-paderborn.de/ihd/content/zoom/3082162
Direct JPEG https://digital.ub.uni-paderborn.de/ihd/download/webcache/0/3082162
IIIF https://digital.ub.uni-paderborn.de/i3f/v20/3081557/manifest
IMPORTANT: Image rendered in retrieval system, but downloading external bytes into the local code runtime failed because external host resolution was unavailable. Therefore no actual two-image pixel extraction was run. This is a separate photograph/digitization of the SAME historical plate, not an independent engraving design. Do not claim 7/7 independently replicated.

## Pre-registered input, no optimization
Source SHA-256 bea5f699b53f9306f37708fc81edbd9491ecaf042cd3971c32497c376e0ae21f.
Exactly 256 source cells, 208 active and 48 reserve, previously frozen 109 graph bonds unchanged. Pre-registered seven ink-loop centers I6 I15 K11 M5 N5 O10 P7. The exact V30 original extraction is reused: row/column based 16x16 cell boundaries, 25-pixel axis-aligned ruling exclusion, tile median−36 / max threshold 160, 8-connectivity, small-object exclusion, enclosed white holes area>=2.5px^2 and skeleton junction clusters. 20 sensitivity settings = crop margins 4,5,6,7 times threshold deltas -10,-5,0,5,10. No training on the unseen image.

## Test execution, all claims scoped
- Fresh original-source exact self-check PASS: all 208 per-atom canonical hole counts and junction cluster counts exactly match Test030; every one of 208 per-atom hole and junction 20-setting survival counts also exactly matches Test030. Recovered all 7/7 original stable loops, none extra; original junction-bearing sites 113; no double-loop candidates.
- Synthetic artificial 340x340 image reduced from the same source raster, perturbed by Gaussian pixel noise and placed in a page frame: only **4/7** frozen anchors recovered (I6 K11 O10 P7), and only 5 stable loop sites in total; 110 junction-positive. This is a transport/resolution stress test, NOT independent evidence and should NEVER be cited as an archival result.
- Interactive single-file HTML: original 256-cell image, all 7 frozen anchor highlights, loaded second page, four crop parameters, side-by-side alignment, local-file export. Live archive URL is only a convenience; image CORS may prevent export. Interface permanently labels second-scan measurement PENDING. Chromium Playwright PASS 9/9 checks, zero JS page errors, JS node --check PASS.
- Python script --self-check/--demo/--scan/--fetch, Windows batch helper and local original frozen CSVs included in 16-file ZIP. ZIP SHA256 **90111a07ea14bf0000db749f1200c55d7d12263531294aef57fc5b8cbdfa9fbe**, manifest hashes and ZIP CRC PASS.
- Legacy EE wrapper is absent from all new Test032 derived text files. Original raster and prior append-only audits are unchanged.

## Decision
Engineering: PASS. Provenance: candidate independent photographic/digitization source identified. True out-of-sample ink loop morphology replication: **PENDING**. No empirical claim of DNA, physical atoms or causal time geometry. Upcoming gate: load actual archive page JPEG, register 16x16 grid without data-fitting, measure 208 source cells and the seven frozen anchors under the fixed 20 settings; report native scan resolution and misalignments, not merely a matching illustration.

Artifact: lagado_replication_v32_bundle.zip (Python, standalone UI, frozen source CSV, exact self-check CSV and JSON, artificial stress-test CSV and JSON, script, technical report, test, preview).
AUDIT::APPEND_ONLY::REPLICATION_PENDING