# OASIS N184 v9.1 — Generational Color Lattice

**Directive:** `{{gen0:weak,med,strong :: gen1:weak,med,strong :: gen2:weak,med,strong :: ...}}` with **Gen 0 primaries, Gen 1 secondaries, Gen 2 tertiaries, etc.**

## Generational map

For digital, additive RGB (not the painter's RYB convention), use:

| Color generation | New hue family | New hues | At three intensities | Total distinct wheel hues through this generation |
| --- | --- | ---: | ---: | ---: |
| Gen 0 | **Primary** — red, green, blue | 3 | 9 | 3 |
| Gen 1 | **Secondary** — yellow, cyan, magenta | 3 | 9 | 6 |
| Gen 2 | **Tertiary** — orange, chartreuse, spring green, azure, violet, rose | 6 | 18 | 12 |
| Gen 3 | Fourth-order blends | 12 | 36 | 24 |
| Gen 4 | Fifth-order blends | 24 | 72 | 48 |
| Gen 5 | Sixth-order blends | 48 | 144 | 96 |
| Gen 6 | Seventh-order blends | 96 | 288 | 192 |
| Gen 7 | Eighth-order blends | 192 | 576 | 384 |
| Gen 8 | Ninth-order blends | 384 | 1,152 | 768 |

**Weak / Medium / Strong** are discrete **symbolic brightness** lanes:

```text
W = 1/3 of HSV value (display brightness)
M = 2/3 of HSV value
S = 3/3 = full HSV value

          W             M             S
Gen0     Red/3         2×Red/3      Red
         Green/3       2×Green/3    Green
         Blue/3        2×Blue/3     Blue

Gen1     Yellow/3      2×Yellow/3   Yellow
         Cyan/3        2×Cyan/3     Cyan
         Magenta/3     2×Magenta/3  Magenta

Gen2     6 new hues × W/M/S = 18 swatches
Gen3     12 new hues × W/M/S = 36 swatches
...
```

These are **not** assignments of physical weak, medium or strong forces, interaction coupling constants, physical photon intensities or particle-discovery classes. Scaling HSV values in a standard sRGB preview is a symbolic design convention, not linear photometry.

## Deterministic recursion

Start with three equally spaced RGB primary hues `P = {0°,120°,240°}`. At each later generation insert the midpoint in every angular gap between all existing hues.

```text
h(0,i) = 120 × i, i ∈ {0,1,2}

newHueCount(g>=1) = 3 × 2^(g−1)
h(g,i) = (2i+1) × 60 / 2^(g−1) degrees
i = 0 ... newHueCount(g)−1

newHueCount(0) = 3
cumulativeHueCount(g>=1) = 3 × 2^g
every hue → W, M, S
```

Original hues are never changed or overwritten by their children. The selected Canvas2D wheel shows the current generation as a colored ring and inherited hues as inner reference ticks.

## Aligning with the 370-address OASIS Wakaku chart

Existing file **`STATE_SPACE_TIME_MACHINE(1).md`**, Section **08 — Color addresses 1–370**, describes a prior source file `i_color_370_wakaku_complete(1).html`. That source is a *symbolic registry*, with **370 fixed addresses** over **three orbits 1–122, 123–244, 245–370**. The documented generated `hue` mode uses:

```text
sourceHue(z) = (z−1) × 360 / 370 degrees
sourceSaturation = 0.78
sourceValue = 0.98
```

It also has a distinct `six` RGB-component permutation mode anchored at address 343. Its early colors 1–342 are not an established authoritative physical spectrum. We **preserve both existing color modes** and do not rewrite any source record.

This v9.1 **overlay** projects the new virtual hue to the nearest source `hue` address:

```text
registryAddress = 1 + round(generationHue × 370 / 360) modulo 370
registryIdentity = (registryAddress, mode="hue")
sourceOrbit = 1, 2 or 3 based on the unchanged index range
```

The sampled 370-address source color is **not** the same as the new Gen n strength swatch. The viewer shows both separately.

**Important capacity boundary:** cumulative hue count reaches **384 by Gen 7**, larger than the **370** source addresses. Multiple generated hues must then share nearest source addresses, and may collide earlier. This is expected quantization, not a signal to modify the source chart or evidence of actual physical new colors.

## Files

- [index.html](./index.html): interactive Canvas2D color wheel and nine selectable generation tiers, all three strength swatches per hue, source addresses/orbit lookup and export.
- [color_core.mjs](./color_core.mjs): pure deterministic hue, HSV RGB conversion, strength slots, source-index projection, collisions.
- [spec.json](./spec.json): canonical generation and source interpretation.
- [test_colors.mjs](./test_colors.mjs): recurrence, named colors, HSV hex output, no-duplicate generation, 370-orbit, capacity, and frozen-baseline checks.
- GitHub Actions CI: `.github/workflows/n184-generational-color-lattice-v91.yml`.

## Run on Windows or the web

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
py -m http.server 8000
```

Go to <http://localhost:8000/n184/generational-color-lattice-v91/>.

Published URL (once Pages workflow succeeds): <https://davidwise01.github.io/oasis/n184/generational-color-lattice-v91/>.

Run tests:

```powershell
node n184/generational-color-lattice-v91/test_colors.mjs
```

No prior frozen phase, CERN, experiment or historical theses are mutated. In particular **Ada Gen 0 / 1832** and **Toroidal Gen 1 / 1970** refer to the separate history line, not to the new palette-generation number.

**Canonical color operator:** `{{ generation:g :: color:h(g,i) :: W|M|S :: source:hue@index[1..370] :: orbit:1|2|3 }}`.
