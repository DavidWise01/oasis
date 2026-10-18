# N184 Canvas2D viewer — FINAL FREEZE

**Declaration:** 2026-10-18
**Status:** Feature-complete and intentionally frozen for the current scope. No additional kernel work or renderer experiments authorized in this baseline.
**Production renderer:** Canvas2D (default).
**Optional experimental renderer:** WebGL2 (not certified for default).
**Live viewer:** https://davidwise01.github.io/oasis/n184/blueprint-lab-v63/

## Frozen feature boundary

- N184 v6.1 kernel and recovery baseline remain frozen separately; they are **not modified by this freeze record**.
- 16 vertices, 32 tesseract edges, 38,400 reversible address/nibble state pairs.
- 4D geometry / 3D projection / Canvas2D drawing, four views, shared-scene cache, dirty-frame scheduler, slice/orbit/idle modes, inspection and export utilities.
- Canvas2D is selected as the **production display backend**; no GPU switch is required.
- No claim of physical quantum/atomic validation, power-loss durability, long-duration uptime, pixel-perfect WebGL2 parity, or certified browser FPS.

## Canonical tracked source blobs at freeze declaration

The following **Git blob SHA-1s** were retrieved directly from GitHub on 2026-10-18. Blob hashes describe individual file contents; they are not whole-release SHA-256 digests.

| Path (relative to `n184/blueprint-lab-v63/`) | Git blob SHA-1 |
| --- | --- |
| `geometry.js` | `52e3598f026ac5278024d0f98a460e6eb1f0a692` |
| `shared-scene.js` | `c9c332f027443c6a9a63614c113427bdcb64adaa` |
| `dirty-render.js` | `8c7325f4f076a85b708278337749f3ad8029a419` |
| `app.js` | `f05fc9272512fc68180533ff20438f18a4b0fa80` |
| `index.html` | `3ce8c207e99c098156b2b2e356ca7c02bbe72561` |
| `webgl-option.js` | `3164c2cac8555150d8029ba38145b6cfb7e60b16` |

Other supporting scripts and assets are preserved in the Git commit that contains this manifest. For a full historical snapshot, check out the pinned freeze commit or the archival branch instead of following moving `main`.

## Verification evidence

- Final CPU preparation benchmark: [CANVAS2D-PRODUCTION-BENCH-20261018.md](./CANVAS2D-PRODUCTION-BENCH-20261018.md) — 600 frame evaluations × 3 trials for orbit, idle and slice; idle 599/600 frames skipped.
- Historical software integrity baseline: [v6.1 certificate](../certification-v61/FREEZE.md).
- Browser WebGL2 experiments are separately documented; these do **not** supersede the Canvas2D renderer selection.

## Preservation policy

This is an **append-only freeze declaration**. No existing source files are changed by this commit. Future improvements, if ever requested, should use a new version or branch rather than altering this canonical snapshot.

Git commits are content-addressed and an archival branch can pin the snapshot, but this does **not** make `main` technically unwritable. Strong repository-level immutability requires GitHub branch/tag protection and permissions (or externally retained copies). No claim is made that those controls were enabled.
