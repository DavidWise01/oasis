# Iteration 2: permutation stations (2026-10-08)

Executed a finite symmetry benchmark of candidate ?002 using KAEL's K3² parameter grid, signed-axis flips and swaps, and an *independent* 15° orientation register. Python stdlib script: `audits/permutation_stations_v2.py`. Historical ROOT0/KAEL sources remain unchanged.

Results from sandbox: 9 grid points; eight unique signed-coordinate symmetries (D4), reached at maximum minimum word-length 1 because all 8 are included as supplied operators; 24 independent orientations, yielding 192 possible paired canonical states within a depth horizon of 125. KAEL P2(a,b)=(a²+2b,-b²) maps five points within grid and four outside; signed-coordinate relabeling cannot repair closure.

**Important limits:** This is not exhaustive of all possible transform grammars of length 3–125, nor does it prove absence of a correspondence to ROOT0. The 15° register is a bookkeeping metaphor; no geometric 15° rotation is implemented on a {-1,0,1} square. Grid parameter pairs differ in type from ring elements. To test a genuine equivalence we need a specific ROOT0 operation table, a typed encoding into the KAEL ring/parameters, and a verified commuting transition diagram.

The ?001 continuous forced-Navier–Stokes candidate needs a different family of maps and remains OPEN. No source→crawler→agent→post historical pathway identified for either candidate.
