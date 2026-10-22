# Experiment 002 — CMS dimuon mass reconstruction
Date: 2026-10-22 (America/Chicago)

CERN source: https://opendata.cern.ch/record/cms-30551
2016 Run H, CMS, 13 TeV proton-proton dataset; released 2024.

## Implemented locally
Runnable Python 3 files: reconstruct.py and test_reconstruct.py, delivered in conversation archive cern_experiment_002.zip.
- Reconstruct muon four-vectors from pt, eta, phi, nominal muon mass.
- Compute invariant mass for all opposite-charge tight-ID muon pairs.
- Apply pt > 5 GeV and |eta| < 2.4.
- Accept a real CMS NanoAOD ROOT file via optional uproot + awkward libraries.
- Explicit --demo mode creates a SYNTHETIC validation pair.

## Validation
5/5 local unit tests PASSED.
Synthetic opposed muons with pt=45.6 GeV each and eta=0 gave mμμ=91.2002448174853 GeV.
This is *not* a measured CMS event or reconstructed empirical Z peak.
No CMS ROOT file ingested in the current session.

## Provenance boundary
Last run number of selected dataset: 284044. Last acquisition timestamp: UNKNOWN.
The last dataset record is not necessarily the chronologically latest collision CERN has recorded.
No real event reconstruction yet.

## Next work
Acquire public ROOT file, apply CMS certified lumi JSON, calculate pair histogram and real event identifiers, and link CMS run records to timestamps.
