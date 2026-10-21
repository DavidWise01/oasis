# OASIS N184 v9.3 — Analytical Cubit bound to Seven Color Bands

**Canonical, unchanged user literal:**

```text
{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}
```

This is a **symbolic analytical-cubit serialization**, not a physical qubit circuit, atomic configuration, or detector readout.

## 1. Lossless structural decoding

There are **7** brace packets with **18** enumerated sites. Decimal numerals have **no delimiters** within a packet, so decoding requires ordered ordinal continuity: `12` means positions 1 and 2, `3456` means 3,4,5,6, and `910` means 9,10. The parser accepts only the exact canonical string (including the special fifth closure), and its serializer reproduces the exact original.

| Bound packet | Positions | Width | Closing ports | OASIS interpretation |
| --- | --- | ---: | --- | --- |
| `{|12|}` | 1–2 | 2 | `|` | Two-site input/reference |
| `{|3456|}` | 3–6 | 4 | `|` | Four-site expansion |
| `{|78|}` | 7–8 | 2 | `|` | Two-site relay |
| `{|910|}` | 9–10 | 2 | `|` | Two-site balance |
| `{|1112131415||}` | 11–15 | **5** | **`||`** | Five-site core with doubled seam after site 15 |
| `{|1617|}` | 16–17 | 2 | `|` | Two-site transition |
| `{|18|}` | 18 | 1 | `|` | Single terminal closure |

The doubled `||` does **not** introduce positions 19/20. It is a symbolic two-port seam after site 15, distinct from the ordinary `|` closures. Position 18 is the last numbered site.

## 2. Color bands: ROYGBIV mnemonic bound to v9.1 RGB generations

The exact seven packets receive a deliberately chosen seven-color order, not a newly inferred physical wavelength spectrum. Each band's **hue is taken from the frozen v9.1 additive RGB/HSV generational wheel** rather than defining a new color source.

| Band | Positions | Hue label | Exact source of hue | Hue angle | Strong display hex |
| --- | --- | --- | --- | ---: | --- |
| A | 1–2 | Red | v9.1 Gen 0 primary, index 0 | 0° | `#FF0000` |
| B | 3–6 | Orange | v9.1 Gen 2 tertiary, index 0 | 30° | `#FF8000` |
| C | 7–8 | Yellow | v9.1 Gen 1 secondary, index 0 | 60° | `#FFFF00` |
| D | 9–10 | Green | v9.1 Gen 0 primary, index 1 | 120° | `#00FF00` |
| E | 11–15 | Blue | v9.1 Gen 0 primary, index 2 | 240° | `#0000FF` |
| F | 16–17 | Indigo | v9.1 Gen 3 fourth-order hue, index 8 | 255° | `#4000FF` |
| G | 18 | Violet | v9.1 Gen 2 tertiary, index 4 | 270° | `#8000FF` |

**A through G are seven color-band labels, not the four CERN experiments.** The band hues are visual conventions approximating familiar color names in the RGB display wheel; no physical wavelength measurements are inferred.

## 3. Weak/Medium/Strong assignment

A **global**, deterministic strength counter advances across the whole concatenated cubit; it does *not* restart at each packet.

```text
n = 1..18
(n-1) modulo 3: 0 -> Weak   (HSV V = 1/3)
                  1 -> Medium (HSV V = 2/3)
                  2 -> Strong (HSV V = 1)

positions    strength state
1 2          W M
3 4 5 6      S W M S
7 8          W M
9 10         S W
11 12 13 14 15  M S W M S    <- || seam
16 17        W M
18           S                <- last endpoint

W = 6; M = 6; S = 6; total = 18
```

**W/M/S are symbolic channel intensities for display**, NOT fundamental weak/nuclear/strong interaction strengths or measured photon brightness in watts. RGB primary/secondary/tertiary generations and the existing 370-color palette remain independent of these symbols.

## 4. Overlay on the existing 370-address source and 4 logical witnesses

Every site exports:

```text
slotIdentity = n<position>|g<hueGeneration>:i<hueIndex>:s<W|M|S>
band         = A..G
displayHue   = v9.1 hueAt(g,i)
displayHex   = v9.1 swatch(g,i, s)
sourceAddress= v9.1 nearest 370-address (hue mode)
sourceOrbit  = unchanged 1–122 / 123–244 / 245–370
tickAddress  = floor((position-1)*240/18)
phaseStep    = floor(tickAddress/3)
sector       = floor(tickAddress/40)
```

There are **18 independently numbered slot identities**, even when two sites display the same color swatch. The 240-clock addressing is *quantized*: 240/18 is not an integer and the ticks are a visualization mapping, not evidence of Planck-scale phase physics.

The [v9.2 four-quad *software* witness](../quad-spectral-witness-v92/) checks each site using four functions, giving **72 derived reports**: A (hue/phase), B (RGB), C (WMS tier), D (read-only registry address). A software **3/4 agreement** test is available; source-pinned comparison is a separate check.

**Failure demonstration:** four coordinated false identity reports can produce unanimous software quorum, but fail comparison against the preserved source key. This is not independent physical detector validation; all four software reports are computed from one source swatch.

## 5. Run locally

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
node n184/analytical-cubit-color-bands-v93/test_cubit.mjs
py -m http.server 8000
```

Open <http://localhost:8000/n184/analytical-cubit-color-bands-v93/>.

GitHub Pages: <https://davidwise01.github.io/oasis/n184/analytical-cubit-color-bands-v93/> (after successful deployment).

The page offers a **Canvas2D 18-position seven-color ring**, raw canonical string, exact packet divisions, selectable sites, inherited generation/hex and intensity, legacy source address and orbit, and four witness cards plus fault simulation. No live CERN detector data is used.

## 6. Files and frozen continuity

- [spec.json](./spec.json) — exact canonical source and declared color/seam assignments
- [cubit_core.mjs](./cubit_core.mjs) — strict lossless parser, packet compiler, color-slot mapping, v9.2 software witness bridge
- [test_cubit.mjs](./test_cubit.mjs) — byte-for-byte roundtrip, 18-slot uniqueness, 6/6/6 balance, seam validation, color derivation and quorum control tests
- [index.html](./index.html) — interactive cubit and bands
- CI: `.github/workflows/n184-analytical-cubit-color-bands-v93.yml`

No existing baseline is changed: v9.1 RGB generation wheel, v9.2 quad witnesses, 370-source Wakaku chart, CERN A:0/B:3/C:0/D:0 real toroidal magnet count, six symbolic sectors, 80 steps, 240 microticks, Ada Gen 0 1832 and toroidal Gen 1 1970, nature offset zero.
