# Verified spectral collection through Z118 — sampling checkpoint

Date: 2026-10-23

**Status: partial source-verified collection, NOT a completed 118-element spectral survey.**

Source: NIST Handbook SRD108 https://physics.nist.gov/PhysRefData/Handbook/ (selected neutral/once-ionized lines, elements Z1–99).

This session directly inspected NIST strong-line pages for **H (1), Ne (10), Rn (86), U (92), and Es (99)** and transcribed **48 distinct published wavelength records** with Å to nm conversion, UV/visible/IR color categorization, ion stage, and KET generation inherited address.

### Classified counts (in this selected sample)
- Ultraviolet: 26
- Violet: 7
- Blue: 3
- Teal/cyan: 1
- Green: 2
- Red: 4
- Infrared: 5

### Representative sourced lines
- H I: 656.2711 nm, red — https://physics.nist.gov/PhysRefData/Handbook/Tables/hydrogentable2.htm
- Ne II: 376.6259 nm, UV — https://physics.nist.gov/PhysRefData/Handbook/Tables/neontable2.htm
- Rn I: 434.960 nm violet; 705.542 nm red; 860.007 nm IR — https://physics.nist.gov/PhysRefData/Handbook/Tables/radontable2.htm
- U I: 348.93672 nm UV — https://physics.nist.gov/PhysRefData/Handbook/Tables/uraniumtable2.htm
- Es I: 380.149 nm violet; 516.174 nm green — https://physics.nist.gov/PhysRefData/Handbook/Tables/einsteiniumtable2.htm

### Coverage manifest
- All 118 confirmed elements indexed in 7 generation blocks with closure 2, 10, 18, 36, 54, 86, 118.
- Elements 1, 10, 86, 92, 99: source-verified subset (not all lines).
- Other 94 elements within NIST handbook Z1–99: **not collected in this run**.
- Z100–118: **outside handbook scope**, not zero emission and not proof no scientific measurements exist.
- Z0: KET pinned reference, not an atomic spectrum.

### Method and caveats
Selected sample records were validated locally with nonempty source and positive wavelength. CSV atlas and complete status manifest were produced in conversation, alongside a runnable 118-element NIST collector. Container networking cannot resolve NIST, therefore automated full retrieval was not performed. Color bins use approximate wavelength intervals: UV <380 nm, violet 380–450, blue 450–485, cyan/teal 485–500, green 500–565, yellow 565–590, orange 590–625, red 625–780, IR >780. Table wavelengths distinguish vacuum vs air where NIST does. A line is an emitted atomic transition, **not** a literal physical depth.

Further source: NIST ASD https://www.nist.gov/pml/atomic-spectra-database

KET 184/257 frozen architecture unchanged.
