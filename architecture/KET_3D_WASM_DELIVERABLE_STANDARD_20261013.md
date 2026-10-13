# OASIS / KET — 3D WebAssembly deliverable standard
Date: 2026-10-13
Status: user-directed default for future **interactive visual engineering artifacts**. This standard does not mutate the previously frozen KET kernel.

> "everything should be 3d wasm from now on please. can you commit to git and make a generative io page please"

## Forward-build convention
- **Default:** all future interactive diagrams, engineering sheets, engines, visualizations and Generative I/O pages use **real 3D geometry** with a **WebAssembly execution/computation core**.
- **Primary renderer:** WebGL2 in an offline-first browser page; use Canvas2D software **projection of the same 3D WASM geometry** when no GPU context exists. The fallback is not a new 2D physical model.
- **Deliver both:** a self-contained runnable `HTML` and an editable high-definition `SVG` engineering blueprint from the same geometry; include the compiled `.wasm` and original compilable source when delivering a ZIP.
- **Generative I/O:** user-adjustable input JSON, validated register constraints, seeded deterministic state/geometry, play/step/reset and exportable JSON receipts plus traces.
- **Audit:** verify WASM binary validity, compile/replay, deterministic 360+3+3 closure where relevant, exact frozen glyphs, file hashes, JavaScript syntax, and browser interaction. Report GPU visual test limitations accurately.
- **Revision control:** commit new apps to `DavidWise01/oasis` under additive versioned paths, **never edit the frozen 360+3+3 v2.0 baseline or reinterpret its 366-address map without explicit new versioning**.
- **Nonvisual documents and supporting files** (README, audit logs, math, CSV, Markdown) remain standard text/data formats alongside the 3D WASM app; forcing WASM onto prose would not improve execution.
- **No physical overclaim:** a deterministic non-universe toroidal controller is an abstract model, not a cosmic proof.

## Initial implementation
- [Standalone executable 3D WASM app](../apps/ket-generative-io-3d-wasm-v01/index.html)
- [Compilable C/WebAssembly core](../apps/ket-generative-io-3d-wasm-v01/src/ket_io_core.c)
- [Input/output and build specification](../apps/ket-generative-io-3d-wasm-v01/README.md)
- Frozen kernel pin `de8f8b80aba3a73dd371811f6b4be39df92e45ce`
