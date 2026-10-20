# OASIS N184 · CERN Four Experiment Ports v8.3

**Prompt:** “alice, atlac, cms, lhcb, yeah 4 torroids makes emergence.”

This is an **observational engineering analogy**, recorded on 2026-10-20 as an additive layer on top of [OASIS v8.2](../arc-phase-duration-v82/). The spelling `atlac` is interpreted as **ATLAS**; four major experiments are **ALICE, ATLAS, CMS and LHCb**.

## Four independent detector sites around one accelerator

| Experiment | Collision point | Role | Detector magnet layout |
| --- | --- | --- | --- |
| ATLAS | IP1 | General-purpose particle physics / Higgs | central solenoid, barrel + end-cap toroids |
| ALICE | IP2 | Heavy-ion collisions / quark–gluon plasma | solenoid + dipole |
| CMS | IP5 | General-purpose, independent design | large solenoid |
| LHCb | IP8 | Heavy-flavour and matter–antimatter measurements | dipole |

**Correction:** These are **four experiments, not four physically identical toroids**. ATLAS uses toroids; the magnet structures of the other three differ. They sit at separate accelerator collision points and do **not** all record the same collision event.

Primary CERN sources:
- CERN experiments: https://home.cern/science/experiments/
- CERN experimental areas/magnets report: https://cds.cern.ch/record/1038089/files/lhc-project-report-1009.pdf
- ATLAS magnets: https://www.atlas.cern/Discover/Detector/Magnet-System
- CMS solenoid: https://home.web.cern.ch/science/experiments/cms/

## Four-witness correspondence (symbolic)

```text
               ATLAS [IP1] — general-purpose witness
                  |
    ALICE [IP2] — RING — CMS [IP5]
                  |
               LHCb [IP8] — heavy-flavour witness

four independent experimental observation locations
one shared accelerator infrastructure
different measured collisions and complementary questions
```

These positions in the little text diagram are **conceptual**, not geographically accurate ring azimuths.

The analogy for OASIS is **dynamics → evidence from several perspectives → independent checks → reconstructed system-level knowledge**. Collisions and underlying particle interactions create the physical outcomes; the detectors collect data. The observations do **not** imply a four-witness quorum creating particles, prove four-toroid cosmology, or establish any new physical emergence law.

## Preserved OASIS structure

```text
X :: state             Y :: space             Z :: state+time
phase :: 80 steps × 1.25% = 360°
arc :: 6 subdivisions
symbolic exact grid :: lcm(6, 80) = 240 microticks
one bubble :: l_P
conditional duration reference :: l_P / c
```

The 240-microtick software synchronization grid is NOT how CERN's real beam timing is implemented. The real experiments have a much more complex accelerator timing, triggers, and event reconstruction infrastructure.

The four-site overlay is **not** a change to the existing frozen N184 kernel or any previous version.

## Files

- [Machine-readable registry](./spec.json)
- [25 deterministic alignment checks](./test_cern_overlay.mjs)
- [Earlier one-bubble timing model](../arc-phase-duration-v82/)
