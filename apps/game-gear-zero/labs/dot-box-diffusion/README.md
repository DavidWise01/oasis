# DOT :: BOX :: DIFFUSION

A standalone, offline-capable, **live recursive ASCII + RGB diffusion viewer**, using the user's exact four-dot order:

```
.|.|.|.|
```

**Core statement:** The box is the dot; the box is also its diffusion at another scale.

## Run

Open `index.html` in a modern browser. It has **no CDN, imports, game ROM, npm dependencies, external graphics or tracking**. You can also host the directory on GitHub Pages.

### Three components

1. **Prettier ASCII:** A frame for the current parent dot and its four ordered children, plus a scrollable, colorized ASCII terminal. Switch between RGB symbols `.RGYBMCW`, channel density `.:*#`, changed-this-hop wavefront `.+o`, and binary `000..111`. Export/copy ASCII snapshots.
2. **RGB diffusion into recursive boxes:** Each position holds a three-bit mask (`R=1`, `G=2`, `B=4`, eight combinations). A dot expands into **four** child dots; all child boxes retain four ordered terminals `. | . | . | . |`. Seed red at terminal path `000...`, green at `111...`, and blue at `333...`. At each synchronous hop, a node retains its RGB mask and bitwise-ORs the previous hop's masks from its *parent, children and immediately adjacent siblings*. This is a classical graph propagation model, **not** a physical quantum/diffusion equation.
3. **Interactive HTML zoom:** Fold inward (`−`) or unfold outward (`+`) from generation G0 through G6, click a child dot to enter its box, backtrack through breadcrumbs, scrub or play/pause diffusion hops, and inspect transmission versus collapse summaries. The entire program is embedded in one HTML file.

## The recursion

```
G0:  .                         1 terminal dot
G1:  [ .|.|.|.| ]              4 terminal dots
G2:  [ [.|.|.|.|] | [.|.|.|.|] | [.|.|.|.|] | [.|.|.|.|] ]
                                16 terminal dots
G3:  16 × [.|.|.|.|]           64 terminal dots
G4:  64 × [.|.|.|.|]           256 terminal dots
G5:  256 × [.|.|.|.|]          1,024 terminal dots
G6:  1,024 × [.|.|.|.|]        4,096 terminal dots
```

The last `|` is retained as the fourth terminal port; it is *not* automatically a ring closure back to the first dot. A **parent box collapses to one dot** whose RGB summary is the OR of its terminal descendants. We show two distinct readings to avoid conflation: *local transmitted mask* (what has arrived by the current hop) and *collapsed box summary* (OR of descendants at this moment).

Total graph nodes at generation `n` (including all intermediate parent boxes): `(4^(n+1) − 1)/3`. G6 has 5,461 dot/box nodes. The terminal ASCII projection pages the 1,024 four-dot boxes into 16 sets of 64 to avoid a browser lockup.

## Controls

| Control | Behavior |
|---|---|
| `+ UNFOLD / OUT` or generation slider | Expand every terminal dot to a four-dot box; adds one generation |
| `− FOLD / IN` | Collapse one generation, retaining the representative higher-level structure |
| Four clickable dots in the central box | Enter that dot's own box |
| `ROOT BOX`, `PARENT BOX`, breadcrumbs | Navigate the nested box hierarchy |
| Hop slider, play/pause and `+1 HOP` | Advance deterministic synchronous propagation, *not* the generation |
| RGB letters / density / wavefront / binary | Reinterpret the *same current state* as ASCII characters |
| `COPY ASCII` / `EXPORT .TXT` | Export a snapshot of the current generation and hop |
| Arrow keys outside form controls | Left/right hop backward/forward; up/down unfold/fold; Space play/pause |

## Files

- `index.html`: fully self-contained HTML/CSS/JavaScript live viewer. First script tag is a pure `DotBox` model that can be extracted for deterministic testing; second tag is the UI.
- `examples/ASCII-GENERATIONS.txt`: readable G0–G3 and RGB reference projections.
- `tests/test_model.cjs`: pure logic tests via Node.js.
- `tests/test_browser.py`: real Chromium/Playwright integration tests (optional; requires installed Playwright and Chromium).
- `preview-desktop.png`, `preview-ascii.png`, `preview-mobile.png`: tested browser screenshots.

## Validate

```shell
node tests/test_model.cjs
python tests/test_browser.py
```

At this release, **46/46 model cases passed**, plus desktop and mobile Chromium smoke tests for interaction, mode-switching, G6 paging, output export and error-free rendering. This lab is an **independent graphics companion**: it does not modify the frozen Game Gear Z80 emulator or claim to be executing as a `.gg` cartridge.