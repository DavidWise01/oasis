# KET shell puncture atlas — Z0 to Radon (Z86)

Date: 2026-10-23

## Goal
Capture each available measured atomic emission wavelength (not one color per chemical element) and place it into the KET inherited-generation shell register.

## Physical reference
NIST SRD108 Handbook of Basic Atomic Spectroscopic Data, https://physics.nist.gov/PhysRefData/Handbook/ ; tables at `https://physics.nist.gov/PhysRefData/Handbook/Tables/<lowercase-element-name>table2.htm`.

The handbook's strong-line tables cover neutral atoms and first ions and are **selected strong lines**, not complete every-known-transition data. For more complete data use NIST ASD SRD78. Wavelengths may be vacuum or air depending on range. Intensities depend on excitation.

## KET generation register
- Z0 = symbolic pinned reference (not an atom, no emission).
- G0 H–He (Z1–2), closure He(2).
- G1 Li–Ne (Z3–10), inherits G0, closure Ne(10).
- G2 Na–Ar (Z11–18), inherits G0–G1, closure Ar(18).
- G3 K–Kr (Z19–36), closure Kr(36).
- G4 Rb–Xe (Z37–54), closure Xe(54).
- G5 Cs–Rn (Z55–86), closure Rn(86).

Each `|` closes and inherits all previous generations. Store *every retrieved spectral line* as an observation with Z, spectrum/ion, wavelength, region/color, and generation. The same color can occur in many elements and generations.

Approximate wavelength mapping: ultraviolet <380 nm, violet 380–450, blue 450–485, teal/cyan 485–500, green 500–565, yellow 565–590, orange 590–625, red 625–780, infrared >780. Boundaries are analytical bins, not sharp physics.

## Status and provenance
- A downloadable executable Python collector (`shell_puncture_0_86.py`) and its local offline parser unit test were produced in the associated ChatGPT work session.
- Offline syntax and unit test PASS, validating a known hydrogen line fixture against UV and red classification.
- **Full 1–86 spectral retrieval NOT completed in the current runtime:** network DNS was blocked. There are therefore no claimed full-atlas line counts or invented element colors.
- To collect full measured source data, run the Python collector in an internet-enabled Python environment; it writes `transitions_1_86.csv`, `coverage_1_86.csv`, and `summary.json`. A missing-coverage row must remain missing.
- This is an electron-emission-spectrum mapping, not evidence that an atom mechanically contains nested preceding atoms or that observed wavelengths physically reside at the Planck length.

Frozen KET 184/257 baseline unchanged.
