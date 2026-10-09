# P3.17 — Million-seed collision-free address routing
Tested 2026-10-09, Node local execution: PASS 1,000,000 unique routes, all reversible. Ten immutable Stargate position tokens `00 11 22 33 42 24 33 22 11 00` are a prefix; a six-base-11-character suffix assigns each integer seed 0 through 999,999. Six digits have capacity 11^6=1,771,561 (771,561 unused), final seed 999999 encodes `623350`. This is a formal addressing convention added to the user's notation, not an assumption that the ten glyphs alone uniquely encode the million seed IDs. Seeded cross remains `(-2,+3),(+2,-3)` centered on label `0vwxyz`, with `{{5.5}}^{{5}}` scale retained in the parent P3.16 module and `-+- /\\ +-+` symbolic dual branches.

Also tested modulo 4096 bucket routing: 4096 occupied buckets, 995,904 repeated bucket assignments, max load 245. Full addresses do not collide; lossy buckets do. No infinite vogel/voxel/vector domains were enumerated; this is not evidence of a physical Stargate or Planck-scale transport.

Run in Node: `node docs/reality-tensor/dyson-inversions/test_p317.mjs`.
