# A.I.O.N. × ALON SAPPHON — i :: 3D / Fault Isolation / Sheet 019

**Status:** Additive, self-contained, runnable visualization and deterministic graph fault engine. No changes to frozen K.E.T. source, ALON chemistry, or reference atom coordinates.

## Run

Open `index.html` in a modern browser. Software canvas fallback works without WebGL. `index.html` embeds the actual ALON reference coordinates, lattice bonds, and recorded **synthetic** pulse trace; it makes no external requests.

Choose two atom IDs and use the fault controls to disable a specific reference link, break the current route, remove 42 periodic bonds, isolate the source atom, or restore all links. The shortest path and connectivity numbers update immediately. A disabled contact renders as a broken red segment in the lattice; current route highlights in gold. The fault log increments per state change, and the view receipt includes this local event history.

**Important scope:** Faults affect an *undirected quotient graph* of the 55-atom reference cell. In 2×2×2 and 3×3×3 displays, each reference link failure is repeated across all matching cell copies. Outer stubs are visual representations of periodic translations. No atom/bond geometry changes. The SAPPHON ring, vessel, and color anchors remain symbolic overlays.

### Reference results

- 55 occupied atoms and 122 distinct Al–anion graph contacts.
- 42 periodic-wrap reference contacts, 80 internal.
- 0 graph bridges; all 122 single-link cuts preserve connectivity.
- All 7,381 two-link cuts preserve connectivity. Global edge-connectivity is exactly **3**, since the three incident edges on site 24 isolate that site.
- Remove all 42 wrap contacts: connected component sizes `[52,1,1,1]`.
- Disable link `24–7`: route from 24 to 37 remains six hops. With ascending neighbor order the viewer picks `24,9,25,6,26,14,37`.
- Isolate source 24: 119 active edges, component sizes `[54,1]`, no route from 24 to 37.

## Files

- `index.html`: offline canvas with WebGL2 and 2D fallback, controls, 55/440/1,485-atom tiling and synthetic pulse playback.
- `AION-SAPPHON-SHEET-019.svg`: technical blue-paper 4800 × 3000 editable vector drawing.
- `AION-SAPPHON-SHEET-019.png`: preview (2400 × 1500 raster).
- `AION-SAPPHON-019-dashboard.png`: browser-tested interactive frame.
- `audit_019.py` and `audit-results.json`: independent stdlib all-single/all-double-link fault audit.
- `manifest.sha256`: integrity digest listing; provided in release ZIP.

## Reproduce

```bash
python audit_019.py
```

The browser build is a new **sapphon/v3** module under the existing `projects/xenonite-x0/alon-separate/ket-aion-runtime/` path. It does not alter the sealed K.E.T. kernel or the earlier `sapphon/v1` and `sapphon/v2` releases. Graph receipts are local observations and do not modify the production WAL.

This is structural/network modeling, not an assertion that ALON is a manufactured transistor or that bond failures operate as reliable physical switches.
