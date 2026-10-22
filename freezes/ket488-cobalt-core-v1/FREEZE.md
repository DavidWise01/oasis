# KET-488 / Co·0 — cobalt-core v1 freeze

**Frozen on:** 2026-10-22
**Repository:** [DavidWise01/oasis](https://github.com/DavidWise01/oasis)
**Status:** FROZEN REFERENCE — preserve these files exactly. Any future development should occur outside this directory, leaving this baseline unchanged.
**Scope:** standalone self-contained HTML and matching complete JavaScript replacement.

## Byte-for-byte preserved artifacts

| Artifact | Frozen path | GitHub blob SHA-1 | UTF-8 size |
| --- | --- | --- | ---: |
| Interactive HTML | `freezes/ket488-cobalt-core-v1/ket-488-tesseract-agent.html` | `461fcaf0cabf0ca458a56e630c4193dc7cf25bd2` | 42,070 bytes |
| Complete JS | `freezes/ket488-cobalt-core-v1/ket-488-tesseract-agent.full.js` | `a53a9ac40169d672c07195065f5023454379e6a4` | 25,082 bytes |

The freeze copies were fetched again after commit and confirmed identical to the then-current working files, including exact Git blob IDs. The complete JavaScript equals the inline `<script>` content in the standalone HTML.

## Frozen topology and behavior

- **Geometry:** projected tesseract with 16 4D vertices and 32 hypercube edges, animated on a Canvas 2D surface.
- **Vertex registers:** 16 installed selectable vertex nodes; each carries `{{3×3}}^{{3}} = 9³ = 729` symbolic local states, for **11,664 vertex-state addresses**. These do not constitute 11,664 geometric vertices.
- **Chromatic topology:** 488 selectable KET addresses, grouped into four roots of 122 each. Procedural colors are not asserted to be measured elemental wavelengths; import/export remains available.
- **Cobalt center:** `Co·0` at the pinned zero origin `(0,0,0,0)`. Display cobalt is `#0047AB`. Canonical five-wrap symbolic vessel: `((((( wx0yz )))))`.
- **Core links:** exactly **504** symbolic direct source-to-core rays: 16 vertex-node links + 488 chromatic-node links. The 32 tesseract edges are separate.
- **Draw ordering:** radial rays render behind endpoints and the cobalt sphere renders last, on top. A visibility toggle hides the rays without removing their topology.
- **Other retained layers:** independent 8×3 = 24 register, Neon-10 shell 2|8 diagram, and deterministic local agent policies (patrol, trace, harmonize, vertex walk).
- **No remote model or external service:** the agent operates only in the open browser page.

## Freeze checks recorded

- JavaScript parsed successfully.
- Inline HTML script matched the external JS source exactly.
- All statically referenced HTML element IDs resolved.
- Count invariants: 16 vertex nodes, 32 tesseract edges, 488 chromatic addresses, 504 radial links, 729 local states, and 11,664 total vertex-state addresses.
- Existing procedural-color and symbolic-versus-physical boundaries retained.

These are source/static invariants; a live browser rendering or interaction test was **not** independently completed. This freeze commits the source baseline, not a claim of experimentally demonstrated physics or an unalterable GitHub repository.

## Change control

1. Treat these two frozen files and this manifest as **append-only historical evidence**. Do not modify, overwrite, or silently reinterpret them.
2. For new features, edit the active working page or create a new version. Reference this freeze commit and preserve a diff.
3. Use the snapshot's Git commit SHA or frozen-reference branch to recover this precise baseline; a branch name alone is not inherently immutable.
