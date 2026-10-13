# OASIS / KET — 3D WebAssembly deliverable standard
Date: 2026-10-13
Status: user-directed default for future **interactive visual engineering artifacts**. This standard does not mutate the previously frozen KET kernel.

> "everything should be 3d wasm from now on please. can you commit to git and make a generative io page please"

## Rule 01 — six boundaries plus one hole, no external boxes

The user's exact correction to the first rule is **"if you add 4 to 3 you get 6 + a fucking hole"**. Therefore **4+3=7=6+1** means six symbolic boundary positions and one *retained hole*, **not seven solid faces**. For KET toroidal generative I/O, preserve the actual open central passage. Never fill/cap the hole or add another enclosing model-space cage to make the seventh position solid. A toroidal through-hole must be physically present in the scene mesh; arithmetic alone does not generate topology.

This counting rule is independent of the frozen **360+3+3=366** surface/control register. Its six boundary positions are not the six command addresses. Use a real WebGL2/Canvas2D 3D view of an open toroidal mesh driven by WASM; browser rectangular panels are not KET geometric boxes. Future releases must check mesh connectivity/open hole and describe Rule 01 compliance explicitly.

Authoritative corrected contract: [KET Rule 01](KET_RULE_01_NO_EXTERNAL_BOXES_20261013.md).

This is forward-only design guidance. The freeze-pinned v2.0 source and the historical v0.2 application remain unchanged.

## Rule 02 — independent toroids, optional gap I/O

Two KET toroids remain independent KET bodies with their own **4+3=6+one open through-hole**, **360+3+3=366** local addresses and cellular clocks. A separate interface port may be selected at **any of the 360 surface positions on either torus**. Minimum geometric gap is adjustable and is not the same thing as selected-port distance. A software communication gate is selectable **OFF / A→B / B→A / A↔B**; no cross-state messages when OFF. Connecting two ports must **not** merge their parent meshes, fill their open holes, or allocate additional kernel addresses. Gateway events are explicit, directional, deterministic and independently auditable.

See [Rule 02 — Twin Toroids](KET_RULE_02_TWIN_TOROIDS_OPTIONAL_GAP_IO_20261013.md) and the [actual versioned WASM demo](../apps/ket-generative-io-twin-toroids-3d-wasm-v03/index.html). Its WASM and Chromium tests demonstrate optional messaging only within a symbolic computational model, not a claim that physical fields cease to interact when the gate is OFF.

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
