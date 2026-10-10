# Test 042 — LEELUU Paired-Witness 27-Phase Handoff
Date: 2026-10-10
STATUS::EXECUTED::ENGINEERING_PASS::NO_INDEPENDENT_CIPHER_EVIDENCE
PARENT::audits/lagado-leeluu-fifth-element-200-54-2-v41-2026-10-10.md

## Frozen substrate
Exactly 256 original source cells, 200 atoms + 54 operants + witnesses P1/P16; 100+27+1 cells per hemisphere. Four groups of 25 mnemonic CATG atoms per half and all source identities remain fixed. **109** original model-selected bonds retained exactly, including five original cross-hemisphere edges A8-A9, I8-I9, J8-J9, K8-K9, N8-N9. No v40 virtual gate imported and no new physical/source bond added. The original graph has 93 connected components, rising to 98 with the five boundary edges disabled.

## Defined controller — not a decoded feature
26 full phases with complementary six-operant alternating signs propagated into 27-op calendars: left begins -+- and right +-+. In first 26 phases, authorize the five EXISTING crossing bonds on 13 left+ / right- phases and close them on the other 13. The last operant uses two half units, first 0.5{1} with boundary open and witness P1's preparation digest, then 0.5{0} with boundary closed and witness P16's commit digest. Total duration 26+0.5+0.5=27 units, implemented as 54 microticks. This is an explicitly designed symbolic clock, not a demonstrated 27-node Hamiltonian source cycle. Witnesses are controllers, not mass-bearing vertices or independent cryptographic signers.

Probability routing per microtick: retain 0.75 at current atom, distribute 0.25 over traversable unchanged bonds, normalized per atom; isolated atoms retain mass. Uniform baseline opens all five original boundary bonds at all microticks. No code invents connectivity between disconnected model components.

## A7 primary benchmark
After 27 units from A7, right-hemisphere probability is **68.6130534%** with always-open original crossing bonds versus **64.2549255%** with the 27-phase witnessed schedule, difference **-4.3581 percentage points**.
Seven seeds evaluated (A7,A8,I8,J8,K8,N8,F6); F6 right-side mass stays exactly zero because no original graph path connects its component. Other benchmark rows in full local report.
600 independently randomized 26-phase schedules with exactly 13 '+' and 13 '-' per seed, retaining the two fixed half-closing steps and the source geometry unchanged; 4200 shuffled benchmark schedules in total. A7 witnessed right mass exceeds shuffled mean 63.0462% with nominal upper-tail p=0.03494. This is **exploratory**, not corrected for seven seed tests, prior analyses or choice of controller. Not evidence of a time or genetic code.

## Failure and reproducibility
Seven injected failure scenarios: phase 1a, 13b, 26b, 27a, 27b, missing P1, missing P16. All 7 abort their in-process uncommitted transaction, restore the exact initial state SHA-256 and reproduce the uninterrupted final state on retry. They are simulated checkpoint/replay tests, NOT demonstrated crash-durable distributed recovery or true authenticated signatures. Mass conserved every half-tick to <1e-11 and operator remains original-edge-only.
Standalone self-contained Chromium SVG viewer with 256 source cells, 109 original bonds, five marked cross-hemisphere edges, selectable seed A7/F6/I8, mode witnessed/always-open, 54 half-step clock, metadata inspector, witness status. Playwright Chromium **15/15** browser checks, no JavaScript errors.
Full 20-file deterministic ZIP **lagado_leeluu_v42_bundle.zip** SHA256 **a8ae334791d534d587f9e50dd07e234c7ff5d28a42083dfab13930ee19a8fdd0**; second identical assembly same digest, ZIP CRC and 19-item member manifest verified. Includes executable Python simulation and viewer builders, test script, source v41 atlas/schedules, frozen v22 edges/nodes, seed/trace/4200-null/fault CSVs, JSON stats, ASCII diagram, full Markdown report, offline SVG HTML, browser preview.
The retired legacy annotation is absent from new derived text and prior source files/records were not modified.

DECISION::CONTROL_EXECUTION_PASS::NEITHER_OPTIMAL_TRANSPORT_NOR_HISTORICAL_ENCODING_DEMONSTRATED
NEXT::TEST043_FAILOVER::measure the minimal original-grid interface redundancy required for loss of one selected cross-hemisphere original bond, keeping any proposed virtual gates labeled separately; or implement and test persistent checkpoint/witness authentication before calling the current in-process rollback production-reliable.