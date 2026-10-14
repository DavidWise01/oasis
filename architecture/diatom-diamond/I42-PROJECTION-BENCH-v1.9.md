# {{i}} projection and carrier benchmark v1.9

The original 42 coordinate-distinct source-token identities (not the OBS44 table) appear in `diatom.mjs` with 8 lane-aware views. Each token participates in 8 × 8 = 64 ordered view pairs, so the full source comprises **2,688** token/view transitions. Projections currently relabel the view metadata and preserve the source address; they do not define a spatial transformation.

The original `|.|.|.|` four-port carrier packs 42 tokens into 11 cells per rail, with a final cell of two occupied and two padded ports; 31 adjacency links are active per rail. The mirrored dual carrier must decode back to the exact original **lane + slot identity**. In particular, `i6:3` and `i7:4` both show `0` but are distinct tokens. `n` in the original `{{i}}` is `i4:2`; it is `00` in the separate OBS44 registry. Those namespaces require an explicit tagged adapter. OBS44 has no glyph `0` entry because `00` means `n`.

## Local repeatable test

A JavaScript dynamic-cell reference and optimized C++ fixed-buffer implementation each processed 2,500 sweeps of all 64 view pairs × 42 tokens: **6,720,000 token/view records per timed run** and 3,520,000 dual-rail carrier cells per run. Both reconstructed both positive and mirrored rails and agreed on checksum `3166452789`, including identity collision safeguards.

Five local runs on one host produced median rates of approximately **7.07 million records/s for JavaScript** and **269 million records/s for C++**. **These figures do not isolate language speed**, because the two implementations differ in allocation, object representation and specialization. They are correctness and implementation-profile evidence, *not* comparable to the OBS44 six-runtime matched benchmark. They exclude OBS coordinate serialization, TCP, network congestion, cryptography, model inference and physical quantum hardware.

## Architecture recommendation

Use coordinate-distinct `{{i}}` token identities as the core semantic namespace, keyed by lane/slot, with source and destination views as tags. Store the 42 addresses in compact `u8` values at runtime and retain their lane/slot metadata through a static verified table. Keep `{{OBS44}}` a separate tagged ingress/egress alphabet and introduce only a lossless, explicitly defined adapter; never conflate glyph `0` or the `n` center across alphabets.

Keep the C++ and Rust candidates from the OBS44 six-language benchmark open pending an exact, same-runner `{{i}}` full-carrier and network benchmark. Correlated mirrored classical rails do not demonstrate quantum entanglement, and view changes cannot remove latency or physical time dilation.

**Frozen `{{i}}` / KET / dual5 v0.7 sources unchanged.** No witness/signature or checkpoint system added.
