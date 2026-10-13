# A.I.O.N. × ALON SAPPHON — `i :: 3D` / Engineering Sheet 018

This additive local HTML dashboard extends the original offline Build 017 WebGL2 / Canvas2D viewer without changing its ALON site positions or bond list.

- Atom selection binds `i::3D::cell(x,y,z)::site(id)` to deterministic crystal coordinates.
- Shortest paths are unweighted BFS on the *55-site graph* using 122 contacts including periodic minimum-image edges. Gold route geometry is overlaid on the same three-dimensional view; a periodic link may leave the drawn box. It does **not** imply electron conduction.
- Pulse player uses *actual saved v1.4 synthetic output*, 0.3 s pulse, fast_20ms protocol, replicate 0 (18 samples). It is never implied to be measured ALON charge.
- The View Receipt button exports a local JSON *viewport observation*. It binds to the prior K.E.T. application receipt event ID, but does not append to production ledger or write GitHub.
- No iodine. No chemistry modifications. No additions to frozen K.E.T. source. SAPPHON vessel is symbolic.

Open `AION-SAPPHON-i3D-DASHBOARD.html` locally in a modern browser (no CDN). Operate the left controls to change supercell size, rotate the viewport by dragging, click an atom to change route source; select target from the right panel.

Requires no Python or Node.js for browser use. WebGL2 falls back to 2D software projection.
