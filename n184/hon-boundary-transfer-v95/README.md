# OASIS N184 v9.5 · Periodic HON Root Gate Boundary Campaign

The next additive target after [v9.4's 366-color carrier](../elemental-hon-color-operants-v94/) is to execute the five retained operants at the only three permitted gate source addresses:

```text
H :: Hydrogen (periodic atomic number Z=1)  1..122
                                            122 → 123
O :: Oxygen   (Z=8)                       123..244
                                            244 → 245
N :: Nitrogen (Z=7)                       245..366
                                            366 ⊣ CLOSED
```

The arrows connect **symbolic source addresses**, not chemical transmutation or real atomic interactions. Their seven-band analytical-cubit projection and the earlier 370-color chart are deliberately different coordinate systems.

## Transfer contract

All source-color input comes from **unchanged** [v9.4 `hon_core.mjs`](../elemental-hon-color-operants-v94/hon_core.mjs). Each transition constructs an immutable source ticket:

```text
ticket = (origin-root, origin-address, W|M|S, ordered-operant-program)
outgoing = operateColor(addressColor(origin,tier), program)

if origin == 122: nativeDest = addressColor(123,tier)
if origin == 244: nativeDest = addressColor(245,tier)
if origin == 366: return CLOSED and no destination
otherwise: reject

incoming = operateColor(nativeDest, program)
record hue/display jump, source key, native target key and guards
```

The target color is **rebased into its own root gradient**, rather than copying the old hue as though it represented conserved photons/energy or changing either elemental identity. The ticket preserves its source identity, W/M/S **label**, ordered operator choices and original position. *Numeric HSV brightness can change* under the user model's Explosion operator; this is not a photometric conservation model.

### Five v9.4 color operants, no additional addresses

| Operant | v9.4 proposed display implementation (unchanged) |
| --- | --- |
| Gravity | Halve the hue offset from that root's anchor |
| Expansion | Scale the hue offset from root anchor by 1.25 |
| Compression | Halve saturation |
| Containment | Clamp hue to the current root's interval and cap saturation at 0.8 |
| Explosion | Rotate hue +45°, restore full saturation, increase display value by 0.2 capped at 1 |

These five names come from an earlier frozen symbolic KET specification; the HSV rules are the independently documented **v9.4 model**, not measurements of physical forces.

### Predeclared validation matrix

The fixed program set comprises **six cases**—the empty/identity program plus **each of the five individual operants**.

```text
3 gates × 3 W/M/S levels × 6 programs = 54 cases
  2 active gates × 3 tiers × 6 = 36 transfers
  1 terminal lid × 3 tiers × 6 = 18 closures
```

The regression tests separately exercise an all-five chain and reversed ordering. Every transfer must enforce exact 122→123 or 244→245 adjacency and preserve original reference/provenance; all 366-origin programs must return **CLOSED** with no `to`, no incoming color and no jump. Interior positions are not allowed to perform gate transfers. Addresses **367–370** remain the preexisting four source-only `hue` palette tail addresses and are not HON destinations; **371 does not exist** in this project.

## Color discontinuities are measured, not hidden

The original zero-operant strong-display colors have these symbolic HSV hue jumps:

| Link | Outgoing source hue | Fresh target hue | Wrapped absolute change |
| --- | ---: | ---: | ---: |
| Hydrogen H122 → Oxygen O123 | 30° | 120° | 90° |
| Oxygen O244 → Nitrogen N245 | 180° | 240° | 60° |
| Nitrogen N366 terminal lid | 290° | **No target** | **N/A** |

After an operant program, each side's native HSV transformation is applied in the declared order, and the resulting angle, RGB channel changes and RGB Euclidean distance are reported. This is an **sRGB display diagnostic**; no physical light spectrum, optical continuity, phase invariance, conserved energy or new particle is inferred.

## 18-site analytical cubit bridge

The existing canonical seven-packet cubit remains **byte-for-byte**:

```text
{|12|}{|3456|}{|78|}{|910|}{|1112131415||}{|1617|}{|18|}
```

From v9.4, six cubit positions sample each HON root. The H→O root link connects **site 6 to 7**; the O→N root link connects **site 12 to 13**; **site 18 maps to the sealed N366 lid**.

**Site 15's `||` remains at N293**. It is an independent five-position *color-packet* seam, not another H/O/N root boundary. The 18 sites' original seven band colors and their W/M/S assignments are unchanged.

## File inventory and local reproduction

- [spec.json](./spec.json): fixed gate configuration, program set, provenance, scientific boundaries
- [boundary_core.mjs](./boundary_core.mjs): strict gate validation, immutable tickets, root-native display rebasing, angle and RGB discontinuity metrics, survey and cubit seam audit
- [test_boundary.mjs](./test_boundary.mjs): boundary/atomic-number tests, no-wrap, noncommutative operator order, color jumps, 54-case survey and frozen upstream baselines
- [index.html](./index.html): Canvas2D three-root viewer with gate selector, W/M/S controls, interactive five-operator chain, raw color comparison and per-gate provenance
- CI workflow: `.github/workflows/n184-hon-boundary-transfer-v95.yml`

On Windows:

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
node n184/hon-boundary-transfer-v95/test_boundary.mjs
py -m http.server 8000
```

Visit <http://localhost:8000/n184/hon-boundary-transfer-v95/> or the [GitHub Pages preview](https://davidwise01.github.io/oasis/n184/hon-boundary-transfer-v95/) once deployed.

**Preserved:** v9.1 Gen0–8 generational RGB, v9.2 software witness projections, v9.3 seven-packet bracket grammar, v9.4 H/O/N source gradients, source370 index and its four tail entries, historical Ada 1832 and 1970 toroidal reference, 6/80/240 symbolic ring, and the true real detector toroid inventory of A:0 B:3 C:0 D:0. The H/O/N roots refer to periodic-table elements with real atomic numbers H=1/O=8/N=7, but their 122-address blocks are not verified chemical elements.
