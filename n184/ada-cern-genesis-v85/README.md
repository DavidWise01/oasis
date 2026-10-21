# N184 · Ada (1832) → Toroidal Space Magic (1970) · Thesis v8.5

A historical-source-grounded, interactive two-generation research thesis, **not a claim of Planck-scale or toroidal spacetime physics**.

## Run the interactive viewer

**GitHub Pages:** <https://davidwise01.github.io/oasis/n184/ada-cern-genesis-v85/>

**Windows 11, local:**

```powershell
git clone https://github.com/DavidWise01/oasis.git
cd oasis
py -m http.server 8000
```

Then open <http://localhost:8000/n184/ada-cern-genesis-v85/>.

The page uses one lightweight Canvas2D historical timeline and a 240-microtick symbolic ring; no CUDA/WebGL, dependencies, downloaded fonts or CDN needed. It loads `spec.json` from the same origin, so direct `file://` launching may be restricted by browser security.

## Canonical control surface

- **Gen 0:** 1832, Ada Lovelace, user-selected programming foundation.
- **Gen 1:** 1970, “Toroidal Space Magic,” user-selected cyclic experimental foundation.
- **Epoch interval:** 138 calendar-year labels.
- **Nature offset:** an adjustable visualization parameter `δ_MN`, default 0 years, range −240 to +240. Moving it does NOT rewrite actual historical events.
- **Historical events:** 13 source-annotated timeline entries: Ada meeting and notes, Einstein 1905/1915, Oppenheimer/Trinity, CERN founding, ISR, Unix epoch and 2008 LHC.
- **Symbolic ring:** 6 arcs × 80 phase steps mapped onto 240 exact microticks; four observer labels are software analogies.

## Scientific and provenance protections

CERN was founded in 1954. Its Intersecting Storage Rings achieved the world's first proton–proton colliding beams on **27 January 1971**; 1970 is the selected OASIS Gen 1 epoch, *not* CERN's ISR collision date. Ada met Charles Babbage in **1833**, and published her famous notes in **1843**; 1832 is an anchor, *not* those achievements' dates.

Physical Einstein/quantum claims, military Oppenheimer history and CERN accelerator measurements are **not identical experiments**. They supply distinct historical concepts for testable software design. The symbolic nature offset has no calibrated physical value.

## Files

- [THESIS.md](./THESIS.md): complete thesis, intellectual history, proposed falsifiable experimental protocol and safeguards.
- [spec.json](./spec.json): canonical epochs, chronology, sources, OASIS invariants, unassigned `δ_MN`.
- [index.html](./index.html): responsive interactive chronology, generation buttons, nature-offset slider and ring.
- [test_genesis.mjs](./test_genesis.mjs): deterministic consistency checks of timeline dates, offset semantics, source references, inherited v8.2 model and route wiring.

**Validation:**

```sh
node n184/ada-cern-genesis-v85/test_genesis.mjs
```

Existing lab: [Four-Observer CERN CMS Lab v8.4](../cern-observer-lab-v84/). The next target for the thesis is a fair **held-out reconstruction benchmark**, not mere feature counting.

## Research source bibliography

- [Science Museum Group: Ada Lovelace](https://collection.sciencemuseumgroup.org.uk/people/cp38764/ada-lovelace)
- [Institute for Advanced Study: Albert Einstein](https://www.ias.edu/albert-einstein-brief)
- [US National Park Service: Oppenheimer](https://www.nps.gov/people/manhattan-project-scientists-j-robert-oppenheimer.htm)
- [CERN historical archives](https://archives.web.cern.ch/history_cern/internal_organisation/)
- [CERN ISR](https://home.cern/science/accelerators/intersecting-storage-rings/)
- [CERN first LHC beam](https://home.cern/first-beam-in-the-lhc-accelerating-science/)
- [GNU's 1970 timestamp epoch](https://www.gnu.org/software/coreutils/manual/coreutils.pdf)

All v8.4 and earlier module files remain unchanged. This is a new additive v8.5 thesis module.
