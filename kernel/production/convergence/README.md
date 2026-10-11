# OASIS Convergence — Isomorphic Generative Projection

**Source of authority:** [OASIS-CONVERGENCE-FROZEN-v1.0.md](../OASIS-CONVERGENCE-FROZEN-v1.0.md), committed as `6704945f5ce4474f69c340eef26d3b13d5477c37`. Never silently modify that file. This directory is a distinct, derived implementation.

## Usage
Open a static HTTP server rooted at `kernel/production/convergence/` and visit `index.html` (for example: `python -m http.server 8080`), or deploy these two files to GitHub Pages. GitHub commits publish source, **not** a confirmed live Pages deployment.

- `convergence.js` is a standalone browser ES module with `FREEZE`, `encode`, `decode`, `generate`, `serialize`.
- `index.html` is a responsive emerald UI; enter a seed and a step count, click Generate or Copy Trace.
- The 27 canonical individual states are `3 tracks × 3 timelines × 3 choices`. `encode` and `decode` provide reversible base-three addressing, `0..26`.
- A seeded 32-bit PRNG selects addresses for finite traces. Same seed/count gives the same sequence within this version. It is **not** cryptographic randomness, key material, or signed provenance.
- “Infinite possibilities” means arbitrarily extensible finite sequences; actual UI bounds a single trace to 256 events. No literal infinite computation.
- `{{i.u.us}}` closes each generated trace. This derived view does not mutate the freeze, issue privileged identities, or write to production WAL.
- Exactly three tracks; no new track, layer, or normative law.

## Production acceptance
This is an artifact demonstrating the mapping and a usable interface, **not** production approval of the protected WAL runtime. Existing 0/6 gate status is unchanged. No automated tests were requested or run for this symbolic implementation. For deployable production service work, P0-B01 source import/reproducibility remains open.

## Security
Static site, no service calls, no database, no credentials, no tracking scripts. No promises of cryptographic unpredictability or physical universality.
