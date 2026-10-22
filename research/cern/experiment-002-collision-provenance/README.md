# CERN Experiment 002 — collision provenance

Created: 2026-10-22, America/Chicago (approximately 18:20 CDT).
Location of analysis: remote computational environment, not a CERN detector.

## Verified source
CMS BTagMu Run2016H, 13 TeV proton–proton collisions.
Dataset: https://opendata.cern.ch/record/cms-30551
DOI: 10.7483/OPENDATA.CMS.PQE8.W27O
Recorded: 2016. Published: 2024.
Run numbers: 281613 through 284044.
Events: 28,769,703; 16 files, 29.9 GiB.
Detector location: CMS at CERN LHC, Cessy, France.

## Time semantics
Exact earliest/latest event acquisition date/time: **UNDETERMINED** until timestamps are recovered from run/luminosity mapping or event metadata.
Publication year (2024) is NOT the collision date.
2026-10-22 is the analysis log date, NOT the data acquisition date.
Run 284044 is the maximal run number listed, NOT an extracted latest timestamp.

## Next computation
1. Obtain a manageable authentic NanoAOD file from CERN Open Data.
2. Read Events and Runs and identify max (run, luminosityBlock, event) without treating event number as a clock.
3. Cross-reference CMS run-level timestamps, check UTC/timezone, report precision.
4. Select two muons, form four-vectors from pt/eta/phi/mass, calculate m_ll=sqrt(max(0,(E1+E2)^2 - |p1+p2|^2)).
5. Produce histogram with cuts and provenance, cross-check calibration and uncertainty.
6. Keep stellar H→He fusion and high-energy pp collision studies separate.

References:
https://opendata.cern.ch/docs/cms-getting-started-nanoaod
https://opendata.cern.ch/record/cms-30551
