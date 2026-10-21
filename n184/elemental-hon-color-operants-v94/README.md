# OASIS N184 v9.4 · Periodic HON Roots + Five Color Operants

This is the periodic-table grounding of the earlier [18-position analytical cubit](../analytical-cubit-color-bands-v93/).

## Canonical arrangement

```text
H :: Hydrogen :: atomic Z 1 :: symbolic positions   1..122 :: red → orange
O :: Oxygen   :: atomic Z 8 :: symbolic positions 123..244 :: green → teal
N :: Nitrogen :: atomic Z 7 :: symbolic positions 245..366 :: blue → violet

366 positions = 365 modeled stages + terminal lid at position 366

Five **operants** (instructions, not additional slots):
  Gravity · Expansion · Compression · Containment · Explosion
```

**Important:** Hydrogen's actual atomic number remains 1, Oxygen's 8, Nitrogen's 7. Their names are symbolic **roots of three 122-address carriers**, not a proposal that elements 119–366 are established periodic-table chemical elements. The officially confirmed table reaches **118** elements. See [IUPAC's periodic table](https://iupac.org/what-we-do/periodic-table-of-elements/) and [the recognition of element 118](https://iupac.org/discovery-and-assignment-of-elements-with-atomic-numbers-113-115-117-and-118/).

## 366 versus the earlier 370 palette

The original `MN_PRIME_366_EXPLORER.html` uses **122×3=366** and names its final address the Nitrogen **lid/stitch**. The existing `i_color_370_wakaku_complete.html` source has **370 symbolic color addresses**, including four hypothetical tail positions **367, 368, 369, 370**. Its previous display-orbit indexing was `1–122,123–244,245–370` (last orbit length 126). It does **not** define a new 371st source address.

v9.4 therefore keeps both truths separate:

- **Elemental H/O/N carrier positions:** 1–122, 123–244, 245–366. All three exactly 122.
- **Earlier indexed color display:** 1–122, 123–244, 245–370. The final four legacy positions lie outside the H/O/N 366-carrier model.
- **Five operants:** separately callable manipulations; **no fifth tail slot** is added to either address space.

Neither v9.1's 370-address palette nor the v9.3 cubit's seven original color packets is modified.

## Exact five operator names retained from earlier frozen work

The frozen `KET_TOROID_360_3_3_FULL_SPEC_v2_0_FROZEN.md` specifies five abstract names and descriptions. This module retains those names and implements **newly declared display-only rules**:

| Retained operant | Earlier abstract meaning | New deterministic HSV presentation action |
| --- | --- | --- |
| Gravity | Inward attraction | Halve hue distance toward the H/O/N root anchor |
| Expansion | Outward growth | Multiply hue distance from the root anchor by 1.25 |
| Compression | Inward contraction | Reduce saturation to half |
| Containment | Restorative boundary operation | Clamp hue within its H/O/N interval and cap saturation at 0.8 |
| Explosion | Impulsive outward disturbance | Rotate hue forward 45°, restore saturation to 1, and add 0.2 brightness, capped at 1 |

These are **proposed rendering operations**, not the mathematical dynamics from the frozen source, not measured forces, and not assertions of actual gravity, chemical reactions, or thermodynamic temperatures. The predecessor also uses symbolic 2 K / 1 K / 0 K labels; those remain mnemonics only.

Operants compose **in the order clicked**, up to five steps per sequence. No action changes atomic number, symbolic position, source identity, previous hex values, or the earlier register.

## Binding H/O/N to the analytical cubit

Preserve the exact seven-packet string:

```text
{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}
```

v9.4 adds a **separate** three-root coordinate, sampling **six representative addresses per root** across the eighteen sites. For `n=1..18`, root index `floor((n−1)/6)`; within-root site `(n−1) modulo 6`; corresponding elemental address:

```text
root.start + round((withinRootSite)*121/5)
```

| Cubit sites | Root | Sampled 366-carrier addresses | Strength lanes |
| --- | --- | --- | --- |
| 1–6 | H · Hydrogen | 1, 25, 49, 74, 98, 122 | W M S W M S |
| 7–12 | O · Oxygen | 123, 147, 171, 196, 220, 244 | W M S W M S |
| 13–18 | N · Nitrogen | 245, 269, 293, 318, 342, **366** | W M S W M S |

**Critical seams:** cubit position **15** retains the double `||` after the original Blue packet; its new parallel elemental address is **293/N**. Cubit position **18** retains the seventh Violet packet and additionally maps to **address 366/N**, the terminal lid. These are different types of boundaries, not new physical particles or extra numbered sites.

The original seven packet colors and their RGB Gen0–Gen3 derivation remain frozen. Some original RGB hues differ from the H/O/N carrier gradient. The viewer displays them as **two independent overlays** rather than modifying color names to force them to coincide.

## Files and verification

- [spec.json](./spec.json) — H/O/N boundaries, IUPAC atomic numbers, five frozen names, new display rules, and explicit 366/370 separation.
- [hon_core.mjs](./hon_core.mjs) — all 366 address colors, lossless source index, one to five sequential operant applications, complete eighteen-site symbolic bridge.
- [test_hon.mjs](./test_hon.mjs) — full boundary coverage, atomic-number separation, original color invariants, operators and terminal-lid checks.
- [index.html](./index.html) — interactive Canvas2D 366-color bars, H/O/N root buttons, five operants, W/M/S selection, and seven-packet 18-site cubit projection.
- CI workflow `.github/workflows/n184-elemental-hon-color-operants-v94.yml` (deterministic Node regression).

On Windows 11:

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
node n184/elemental-hon-color-operants-v94/test_hon.mjs
py -m http.server 8000
```

Open <http://localhost:8000/n184/elemental-hon-color-operants-v94/> or the [GitHub Pages build](https://davidwise01.github.io/oasis/n184/elemental-hon-color-operants-v94/) after deployment.

**Frozen and unaffected:** seven cubit bracket packets, source 370-color Wakaku mapping, v9.1 RGB generations, v9.2 software quads, CERN's physical toroid counts A:0/B:3/C:0/D:0, Ada Gen0 year 1832 / symbolic Gen1 year 1970, and the six-sector/80-step/240-microtick model.
