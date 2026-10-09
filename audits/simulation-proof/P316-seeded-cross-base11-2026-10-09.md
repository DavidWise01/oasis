# ROOT0 P3.16 — seeded cross, exact base-11 closure (2026-10-09)

**User correction:** `seeded cross at 10^6 around 0vwxyz x {{5.5}}^{{5}} in crip walk of {{ x - 2 , y + 3 : x + 2 , y - 3 }} = base 11`.

The fixed origin marker is `0vwxyz` (a label, not a resolved coordinate). Cross vectors `(-2,+3)` and `(+2,-3)` cancel exactly. Define `S=(11/2)^5=161051/32=5032.84375`, kept as a rational number; in arbitrary coordinate units the scaled vectors are `(-2S,+3S)` and `(+2S,-3S)`. Their sum is still zero. Base 11 is used as an addressing radix, NOT as proof that a geometric sum mathematically equals eleven. The precise distinction between million seeds and base-11 indexing is preserved: seed indices range 0..999999, and the greatest index encodes as base-11 `623350`.

**Executed local Node.js test:** 1,000,000 unique integer seed indices, round-trip encoding/decoding, canonical antipodal cross closure; plus 100,000 deterministic pseudorandom integer origins and both traversal orders. PASS. Maximum coordinate closure error exactly 0 (integer arithmetic), with malformed seed values rejected.

Two prior `-+- /\\ +-+` channels and the `{-{d}+{+{d}-}}` Dyson topology remain compatible symbolic labels but are **not** assigned a new experimentally validated phase/coupling law by this test. No inference of physical speed, Planck transit, energy extraction, or spacetime dimensions.

Next: P3.17 connect seed indices to the ten Stargate addresses and five nested addressing layers, then test injectivity and collision handling under base-11 hashing without pretending symbolic infinite domains are enumerated.
