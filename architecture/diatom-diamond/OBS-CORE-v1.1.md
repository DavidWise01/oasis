# OASIS / KET — OBS Core v1.1 (witness-free)

Canonical user-authored nested core specification:

```text
{{ specs {{ OBS {{ o 10^10 {{ b 100^100 {{ s 1000^1000 }} }} }} }} }}
```

## Floor
This is the next **additive core specification**, with a symbolic faceted obsidian-glass geometry. Historical signed checkpoints from v1.0 are not part of the active OBS core. **No signatures, audit witnesses, quorums, ledgers, or checkpoint requirement.** The frozen v0.7 `UUDDLRLRBASS × 5` dual-rail floor remains byte-for-byte unchanged; a frozen source comparison is a release regression check, not a runtime witness.

## Arithmetic
- `o`: `10^10` (outer, ten billion addresses).
- `b`: `100^100 = 10^200` (middle).
- `s`: `1000^1000 = 10^3000` (inner).
- Under an **independent-coordinate Cartesian interpretation only**, aggregate `O × B × S = 10^3210` possible address tuples. This number contains 3,211 decimal digits. Valid zero-based indices are `0..10^3210−1`.

Labels outer/body/seed are presentation labels for the ordered `o→b→s` nesting, not claims about physical atomic or crystalline layers. Radii of rendered shells are schematic, **not** physically proportional to the powers of ten.

The JavaScript module `obs-core-v1.1.mjs` provides exact `BigInt` parsing, the three independent scales, a bounded mixed-radix encoder/decoder, and a dual complement:
```
encode(o,b,s) = ((o × 10^200) + b) × 10^3000 + s
mirror(o,b,s) = (10^10−1−o, 10^200−1−b, 10^3000−1−s)
mirror(mirror(p)) = p
```

The implementation does not allocate the entire state space. Symbolic capacity **does not** imply an equivalent number of physical bits, silicon cells, atoms, or entangled quantum states.

## Viewer and validation
The Three.js/OrbitControls HTML viewer renders three nested faceted shells inside the dual five-turn rail structure, with click-to-select shells, visibility toggles, forward/back step playback, integer coordinate input and mirror inspection. Three.js loads from CDN; a 2D Canvas fallback works offline. Tested: local Node.js suite `7,547` assertions (including 2,500 exact large-integer cases), and Chromium offline interaction checks. The remote WebGL path was syntax-checked but **not browser-tested** because CDN resolution is blocked in this environment.

## Files
- `obs-core-v1.1.mjs`: exact indexer/dual complement.
- `obs-core-threejs-v1.1.html`: full interactive 3D UI plus offline fallback.
- Downloadable release ZIP also includes tested benchmark, test results, and an unchanged frozen v0.7 floor source and manifest.

**Material note:** obsidian is naturally occurring volcanic glass. Facets are a design treatment, not a scientific claim that obsidian forms a periodic crystal lattice or realizes quantum hardware.
