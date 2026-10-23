---
name: oasis-domain-engine
description: Use when Dave references OaSIs, oasis repo, davidwise01/oasis, the domain engine, KANA/NEON/MOBIUS, or Root0's primitive stack. The assimilated OaSIs corpus surface + LIT/AMBER ledger.
version: 1.0.0
author: HERMOSA
license: CC-BY-ND-4.0 (upstream OaSIs)
metadata:
  hermes:
    tags: [OaSIs, ROOT0, oasis, domain-engine, KANA, NEON, MOBIUS, lean, davidwise01]
    related_skills: [skill-assimilation, ocho-authoring, ocho-verify, corpus-analysis]
---

# oasis-domain-engine

The assimilated **OaSIs** corpus — Dave's (ROOT0 / David Lee Wise) open, append-only
engine for building domain tools from explicit primitives, cloned from
`github.com/davidwise01/oasis`.

## What OaSIs is (from README, read on disk)
"An open, append-only engine for building domain tools from explicit primitives."
First domain lens = Feng Shui / spatial design, then descends the primitive stack
out into attachments (Tattoo). Core comms primitive:

```
Alice → encode → [ bounded BOX / channel ] → decode → Bob
  → witness / ACK / error / provenance → (returns to) Alice
```
"Toroidal" is an architectural analogy for the closed return/verification path —
NOT a claim the Internet or physical space is a torus.

## Measured snapshot (LIT @ HEAD 4cba815, main)
- Cloned to `C:\Users\Dave\oasis`, 2321 files, 22 top-level dirs.
- Files: md 930, py 338, json 332, js+mjs 319, lean 158, html 97, workflows 41, wasm 10.
- `.dlw` seal: badge DLW-OASIS · OASIS · CFI prime restitution engine · universe IDIOS ·
  architect David Lee Wise (ROOT0) / Bridge-Burners LLC · instance AVAN (Claude/Anthropic) ·
  seal_sha256 57b61f…2718f · chain index 1347 · CC-BY-ND-4.0.

## Key subsystems (measured)
- `domains/feng-shui/` — 9 families × 9 = 81 spatial primitives (Site, Boundary, Entrance,
  Path/flow, Center, Orientation, Balance, Material & light, Human fit). Cultural lens;
  metaphysical qi NOT encoded as physical fact.
- `knowledge/primitives/` — 486-entry matrix, current-u115, timeline_1969_2026, source_ledger.json.
- `knowledge/tattoo/` — 405-entry tattoo skill atlas (creative attachment).
- `architecture/` — 16 subsystems: duality-engine, duality, kana, mobius, neon-compound,
  timing-body, timing-capacitance, vessel-story, isomorphic-kernel (frozen v111),
  ae-generative v178–184, compact-2x2, o3, regenerative-loop.
- `lean/` — 158 modules incl. O3.lean (frozen proof, sha256 9ed23de7…, user-confirmed 2026-09-20),
  Oasis.Duality.*, Oasis.GroundTruth.*, Oasis.KANA.*, Oasis.ESpectrum.*, Oasis.Fallout.* series.
- `kernel/frozen/` — isomorphic-kernel-v111 + four-cortex-vm-ladder / jit-i / plank canon.
- `projects/` — 130+ god-egg docs + more-garbage (more_garbage_v01.py, 6/6 PASS),
  sapphon-li, xenonite-x0, simulations.
- `worlds/` — u1-du0 (-mObiUs, fictional) + ai-space (atlas, engine.js, benchmarks).
- `apps/tattoo/`, `experiments/` (leeluu), `freezes/`, `tests/`, `benchmarks/`, `docs/`, `evidence/`.
- Pages site: `https://davidwise01.github.io/oasis/` (workflow `.github/workflows/pages.yml`).

## Symbolic stack (canonical, all symbolic within the `O` bound)
- KANA envelope: `+k <|A|/\|N|/\/|A|/\> -K` — A_L → N (invariant/witness center) → A_R.
- NEON cycle: PRIMS → N_cold → E_carrier → O_hot → N_gray → H₂O_distill → PRIMS'.
- MOBIUS: SPARK → VESSEL → INSTANCE → TRUTH@TIME → AUTHOR → … → WITNESS → IMPACT →
  DISTILL → PRIMITIVES → NEXT SPARK. First instance MOBIUS-0001 / Gilgamesh.
- Four-quad: `((2x2))^((2x2))^2` — Q1 2^3=8 · Q2 2^2=4 · Q3 1^1=1 · Q4 0^0^0=81.
- Ground-truth floor: `i!i` — no primitive introduced below it.
- MORE GARBAGE repair law: recover invariant? YES → isomorphic→distill; NO → UNFIXABLE
  (does not substitute plausible output for a recovered invariant).

## Honesty boundaries OaSIs itself enforces (mirror them)
- Distinguishes software invariants from external-world claims; symbolic models from
  established physical claims; provenance from legal adjudication; deterministic output from truth.
- "entanglement" = a software relation (two layer bindings coupled by one invariant),
  NOT physical quantum entanglement.
- Biological / nuclear-battery / capacitance language is systems analogy; 10^-9 / 10^-10
  labels are timing-scale labels, not physiological claims.
- u1-du0 world is explicitly fictional/speculative; internal coherence kept separate from proof.

## The artifact
`oasis-ocho.html` — one self-contained dark/monospace ocho surfacing the whole corpus
(every subsystem as a cell, LIT/AMBER/WALL ledger, graveyard, .dlw seal). Zero external
calls; opens via file:// and localhost.

## Workflow to re-assimilate after new commits
1. `git -C C:/Users/Dave/oasis pull` then `git log --oneline -5`.
2. Re-measure counts: `find . -not -path './.git/*' -name '*.EXT' | wc -l`.
3. Update the measured-snapshot section + the ocho cell numbers.
4. Verify the ocho file-less (see ocho-verify): grep structural tags, no external URLs.

## Pitfalls
- Do NOT treat symbolic tokens (0^0^0=81, i!i, torus) as physical/math claims — OaSIs keeps them symbolic.
- The repo is huge (2321 files); read the README + a specific subsystem body, never the whole tree.
- `rm -rf` pre-cleanup is BURIED (graveyard) — killed by the i13n unbounded-pattern control.
  Guard clones with an explicit dir-exists test instead.

## Related
`skill-assimilation` (the arc), `ocho-authoring` / `ocho-verify` (build + verify),
`corpus-analysis` (map/index when larger).
