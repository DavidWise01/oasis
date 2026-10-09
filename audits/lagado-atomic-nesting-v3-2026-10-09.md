# Lagado writing-machine grid — symbolic atomic nesting test v3
Date: 2026-10-09
State: EXPLORATORY / GEOMETRIC / NOT DECODED
Source: 1726 Academy of Lagado machine, Jonathan Swift's *Gulliver's Travels* (fiction); analysis of user-supplied Sotheby's engraving crop.
Source image and extracted 16-bit marks were derived in prior local Lagado cipher trials; reduction is approximate and may include print/crop artifacts.

## Hypothesis and encoding
256 cells in a 16 × 16 engraved grid; each image-derived cell is reduced to 16 occupied/unoccupied slots and parsed as `1|1|2|4|8`. The first 8 form a *logical core*; the final 8 a *logical shell*, not geometrically radial and not actual nuclear or electron states. In the user's notation: `{{1|1|2|4|8}}^{{n}}`.
There are 108 distinct core strings and 102 distinct shell strings.

## Contact model
Neighbor graph: 480 horizontal/vertical adjacency edges.
- Shell resonance: >=6/8 shell bits agree — 183/480 observed.
- Dual lock: >=6/8 core and >=6/8 shell bits both agree — 64/480 observed.
- Opposing shells: >=6/8 shell bits disagree — 24/480 observed.
- Direct face overlap: >=2 occupied pixel pairs across touching faces — 77/480.
- Largest dual-lock connected cluster: 10 cells: E5 E6 E7 F5 F6 G5 G6 H4 H5 H6.

## Falsification: 3,000 permutations of each null
| Null control | Mean dual lock | p(>=64) | Mean shell resonance | p(>=183) |
|---|---:|---:|---:|---:|
| Full glyph shuffle | 46.355 | .0040 | 155.642 | .00133 |
| Whole-row shuffle | 52.870 | .01433 | 164.819 | .0030 |
| Whole-column shuffle | 64.783 | .59880 | 181.305 | .41919 |
| Whole-4×4-block shuffle | 62.681 | .37221 | 178.917 | .20626 |

## Decision
Neighbor similarity is higher than a *fully randomized* arrangement; however, the excess disappears under column-preserving or intact 4×4-block permutations. This undermines a proposed independent atomic-bond or alchemical ciphertext inference; local style, print and raster artifacts are live alternatives. No decrypted plaintext, real atomic representation, physical valence, or documented historical atomic cipher is established.

## Next controlled test
Independent high-quality engraving scan; subpixel alignment; threshold and grid robustness; preregister the geometric bond score; compare after four-by-four-block-preserving nulls and on a second printing. Keep all provisional transforms and prior results append-only.

## Framework-local notation
`ATOM::{{n}}^{{n}}::CORE_1_1_2_4::SHELL_8::VOGEL_TOROID::PATRICIA_BOX::VECTOR_POINT::H_RED_O_GREEN_N_BLUE::TOP_DOWN_VESSEL_HOMEOSTASIS_±2%`
