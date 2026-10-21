# OASIS N184 v9.0 — Four Logical CERN Quads A/B/C/D

**Question:** “Split it into quads A, B, C, D. Tell me how many toroids are in that section and what particles they discovered.”

## Results: actual hardware versus symbolic sectors

| Logical quad | Actual experiment | Real LHC interaction point | Complete toroidal detector magnets | Magnet configuration | Selected particle-related findings |
| --- | --- | --- | ---: | --- | --- |
| A | ALICE | IP2 | **0** | L3 solenoid plus muon-arm dipole | First **evidence** (not established 5σ discovery) of antihyperhelium-4, 2024; characterization of quark–gluon plasma, which is a state of matter rather than a new elementary particle. |
| B | ATLAS | IP1 | **3** | **1 barrel toroid and 2 end-cap toroids**, plus central solenoid | Higgs boson **jointly with CMS**, 2012; B_c*+ excited meson first observed May 2026. |
| C | CMS | IP5 | **0** | Large superconducting solenoid | Higgs boson **jointly with ATLAS**, 2012; Xi_b*0 beauty baryon first observed 2012. |
| D | LHCb | IP8 | **0** | Spectrometer dipole | Pentaquark states (2015), Xi_cc++ baryon (2017), tetraquark exotics and doubly charmed Xi_cc+/Omega_cc+ baryons (2026). |

**Total physically distinct toroidal magnets: 3, all inside ATLAS.** The ATLAS barrel magnet is made of **8 coils**; the **2 end-cap magnets contain 8 coils each**, so there are **24 superconducting coils within 3 whole toroid magnets**. CERN's approximately 27 km LHC accelerator ring (with **two counter-circulating beam paths**) is a different structure; splitting its diagram into four **logical** A–D quads does **not** produce four separate physically closed toroids.

**Not real equal 90° sectors:** The LHC is organized into **8 sectors**. Major experimental points are **IP1, IP2, IP5 and IP8**. The interactive page toggles between OASIS's convenient equal-quadrant diagram and an eight-point *schematic* LHC layout. Actual experiment positions are not equally spaced. Do not interpret angles as real compass coordinates.

## Evidence accuracy

Particle-discovery entries are **selected documented examples**, not a census of all hadrons or particle species, and they are not independent evidence that toroidal magnets cause particle formation. ALICE's 2024 anti-hyperhelium-4 claim has **3.5 sigma significance**, appropriately described as *evidence*, not definitive discovery. The Higgs is one particle species jointly discovered by ATLAS and CMS in 2012. Quark–gluon plasma is a state of strongly interacting matter, **not an elementary particle**.

Historical names and years, magnet counts and status wording in [spec.json](./spec.json) are grounded in primary CERN sources:

- [ATLAS superconducting magnet system (three toroids, each eight coils)](https://atlas.cern/Discover/Detector/Magnet-System)
- [CERN experiment-area magnet configurations (ALICE/ATLAS/CMS/LHCb)](https://cds.cern.ch/record/1038089/files/lhc-project-report-1009.pdf)
- [CERN LHC experiments and technical layout](https://home.cern/science/accelerators/large-hadron-collider/)
- [ALICE first evidence of antihyperhelium-4](https://home.cern/alice-finds-first-ever-evidence-antimatter-partner-hyperhelium-4/)
- [CERN Higgs discovery history](https://home.cern/science/physics/higgs-boson/how/)
- [ATLAS first B_c*+ meson observation, 2026](https://home.cern/atlas-observes-new-composite-particle/)
- [CERN CMS Xi_b*0 discovered in 2012](https://home.cern/lhcb-experiment-observes-two-new-baryon-particles-never-seen-before/)
- [LHCb exotic pentaquarks, 2015](https://home.cern/cerns-lhcb-experiment-reports-observation-of-exotic-pentaquark-particles/)
- [LHCb doubly charmed Xi_cc++, 2017](https://home.cern/the-lhcb-experiment-is-charmed-to-announce-observation-of-a-new-particle-with-two-heavy-quarks/)
- [LHCb double-charm ccd, March 2026](https://home.cern/news/news/physics/lhcb-collaboration-discovers-new-proton-particle)
- [LHCb double-charm ccs, June 2026](https://home.cern/lhcb-discovers-the-final-missing-member-of-a-doubly-charmed-particle-family/)

## Viewer and checks

Run locally in a modern browser:

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
py -m http.server 8000
```

Open <http://localhost:8000/n184/cern-quad-discovery-v90/>.

Published page (after deployment): <https://davidwise01.github.io/oasis/n184/cern-quad-discovery-v90/>.

For deterministic validation:

```powershell
node n184/cern-quad-discovery-v90/test_quads.mjs
```

The viewer uses Canvas2D and the machine-readable [spec.json](./spec.json), with two separate views: **user-selected four logical quads** and **CERN IP1/IP2/IP5/IP8 mapped on an eight-octant schematic**. Changing quad does not modify any historical data or previous code. The previous Carbon-6 3D symbolic mapping, Ada 1832 and 1970 model epochs, 6 arc sectors, 80 phase steps, and 240 microticks remain frozen and are not asserted to be CERN physics.

**Count:** `{{ A:ALICE:0 | B:ATLAS:3 | C:CMS:0 | D:LHCb:0 :: total_toroid_magnets:3 :: toroid_coils:24 }}`
