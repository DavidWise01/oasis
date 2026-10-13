# OASIS / KET — {{i & dd}} mirror-13 lattice v0.5

Derived symbolic language shape, retaining immutable {{i}} identity and original {{d}} carrier. 3D viewer uses Three.js/WebGL over CDN and otherwise falls back to an explicitly identified interactive Canvas projection. This layer is **not** a physical quantum processor.

## User expression (verbatim)

    {-{+{`` 00 11 23 35 48 51 55 55 51 48 35 23 11 00 `` }-}+} x {{ 13 {a-m} x 1 x 13 { n - z } }}

No numerical scale, units, amplitude normalization, probability law, phase angle, or experimentally grounded entanglement relationship was specified. Retain the nested signs as symbolic operators only.

## Derivation

The 14 scalar samples are palindromic. Adjacent differences are

    +11 +12 +12 +13 +3 +4 0 -4 -3 -13 -12 -12 -11

Therefore 13 *ordered transitions* exist. The two alphabet banks have 13 independent indices each, with a single identity pivot, so each transition supports 13*1*13 = 169 address pairs.

    6 × 169 = 1,014 forward sites
    1 × 169 =   169 center-seam sites (55 -> 55)
    6 × 169 = 1,014 return sites
    13 × 169 = 2,197 total symbolic addresses

The coordinate is (step e in [0,12], left a in [0,12], right n in [0,12]). A reversible mirror involution is defined as

    M(e,a,n)=(12-e,n,a)

and preserves the mirror relationship while changing the delta sign. Central layer e=6 has 169 sites, including exactly 13 diagonal self-mirror sites and 78 off-diagonal mirror pairs. The remaining 12 layers form 1,014 pairs, for 1,092 two-element pairs + 13 fixed singleton sites = 1,105 mirror orbits.

## Identity bridge

For the original 42 coordinate-distinct {{i}} tokens from 8 lanes, token ordinal k gets sparse site index `53*k mod 2197`. Since 53 and 2197 are coprime, this is collision-free. Reverse ordinal is `456*index mod 2197`; recover if resulting ordinal is <42. This bridge is an arbitrary deterministic visualization addressing policy, **not** a newly discovered physical mapping, and it preserves lane-qualified duplicate glyphs.

## Quantum capacity distinction

2,197 **symbolic cells** do not imply 2,197 qubits or quantum entanglement. If one assigned each cell to its own orthogonal computational-basis state, minimum qubits is ceil(log2(2197))=12; that yields 4,096 available basis states, leaving 1,899 unused. Defining a statevector, gates, dynamics, or measurements on these states is future work and is not inferred from a palindromic integer list.

## Files

- `mirror13.mjs`: lossless typed address geometry and mirror operator
- `mirror13-benchmark.mjs`: exhaustive round-trip and reflection checks
- `mirror13-threejs.html`: interactive standalone page that loads Three.js r0.166.1 from CDN when online, with Canvas 2D fallback
- `benchmark-results.json`: benchmark output

Run `node mirror13-benchmark.mjs`. For WebGL, open the HTML in a browser with CDN access. Orbit/zoom/pan the structure, select a transition/letter pair, click a voxel, mirror the selection, toggle layers, or auto-orbit. Three.js code uses `InstancedMesh` for all 2,197 grid points.

Frozen KET/isomorphic v111 and the earlier {{i & dd}} 3-qubit simulator remain unchanged. The earlier simulator's three-qubit entropy/CHSH claims must not be attributed to this 13^3 address lattice.