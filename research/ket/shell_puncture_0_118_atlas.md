# Shell puncture atlas expanded: Z0 through Z118

Date: 2026-10-23. Extends the previous Z0–86 experiment through the last currently confirmed chemical element, **oganesson (Og, Z118)**.

## Nested KET inherited generations
| Generation | Atomic numbers | Element walk | Closure |
|---|---|---|---|
| Origin | 0 | Pinned zero, not an atom | 0 |
| G0 | 1–2 | H → He | He 2 |
| G1 | 3–10 | Li → Ne | Ne 10 |
| G2 | 11–18 | Na → Ar | Ar 18 |
| G3 | 19–36 | K → Kr | Kr 36 |
| G4 | 37–54 | Rb → Xe | Xe 54 |
| G5 | 55–86 | Cs → Rn | Rn 86 |
| **G6** | **87–118** | **Fr → Og** | **Og 118** |

The KET `|` closes and inherits every previous generation. 119 element-related addresses, including the nonphysical reference 0. An emitted spectral line is one observation attached to an atomic number, generation, ionization state, and wavelength; no color is assigned without line data.

## Spectral-source boundary
- **Z1–99:** NIST SRD108 *Handbook of Basic Atomic Spectroscopic Data* supplies **selected strong neutral and singly ionized atomic lines** (approximately 12,000 lines across its coverage), **not all known quantum transitions**.
- **Z100–118:** outside this handbook's coverage. This does **not** mean every element above 99 has no experimental atomic spectroscopy; query individual specialist papers/NIST ASD before asserting either known or missing lines.
- **Z118:** oganesson is confirmed as an element; its electron configuration is generally predicted rather than fully measured, and a complete observed visible/UV/IR emission atlas cannot be assumed.
- Period closure is a useful indexing rule; physical spectral data do not imply earlier atoms are literally embedded in later ones.

## Artifact and tests
Companion executable `shell_puncture_0_118.py` distributed with conversation: expanded the earlier 86-element collector to 118 entries, adds G6 inheritance, exposes **not_in_handbook** for Z100–118, writes transitions_1_118.csv and coverage_1_118.csv, and preserves source URLs. Offline parser/gen-index test returned: **PASS: 118-element map, correct noble-gas generation closures, hydrogen UV/visible table parser**.

**Important:** This run did **not** retrieve 118 elements' complete measured spectra or run the full online collector. All absent sources remain marked missing/unsupported, never assigned fabricated wavelength colors.

## Verification
- NIST SRD108: https://www.nist.gov/pml/handbook-basic-atomic-spectroscopic-data/basic-atomic-spectroscopic-data-handbook
- IUPAC confirmed naming of element 118: https://iupac.org/iupac-announces-the-names-of-the-elements-113-115-117-and-118/

Frozen 184/257 baseline unchanged.
