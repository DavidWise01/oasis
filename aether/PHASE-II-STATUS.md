# AETHER Phase II — Live Progress

**Completed: 2 / 8 turns · 25%**  
**Current status: AETHER-097 accepted. Next: AETHER-098.**

| Turn | Bound | State | Cumulative completion |
|---|---|---|---:|
| 1 | 096 Context detection | **Accepted via 096B** | **12.5%** |
| 2 | 097 Context contradictions | **Accepted** | **25%** |
| 3 | 098 Diodic decision path | Not started | 25% |
| 4 | 099 Revocation latency | Not started | 25% |
| 5 | 100 Conditional reauthorization | Not started | 25% |
| 6 | 101 Best-admissible action | Not started | 25% |
| 7 | 102 Homeostatic stress | Not started | 25% |
| 8 | 103 Freeze and closure | Not started | 25% |

## Evidence and completion gate

- Initial AETHER-096 **failed** on old holdout: false promotions 195/14,400 (1.3542%) and added 53 cost units versus rolling. This record is preserved at [096](096/).
- AETHER-096B selected a more conservative threshold **0.72** on validation-only evidence and tested **fresh evaluation seeds 96301–96340**.
- 096B false promotions: **61/14,400 = 0.4236%**, within ≤1% gate.
- 096B burst recall: **508/2880 = 17.64%**, above ≥3% gate.
- 096B economic cost: **123,144.7 vs 123,417** rolling, saving 272.3 units.
- Source, executable test and summary committed at [096B](096b/). Synthetic achievement only; risk bounds under arbitrary drift remain unproven.
- Pages-ready HTML is committed; live Pages deployment must be verified separately.

## AETHER-097 completion evidence

- Untouched final evaluation seeds **97201–97280**, after diagnostic development on separate seeds.
- 16,000 ticks/controller across repeated bursts and burst/decoy changes.
- Contradiction policy revokes stale burst context on a clean audit (≤3 errors).
- False context permission **0.786%**, versus sticky 16.830%; below the ≤1% gate.
- Context revocation delay **0–1 inspection** for all measured exits, versus sticky comparator eight-tick censoring.
- Total cost **124,189.6**, versus sticky **124,561.0**, saving **371.4**.
- Wrong authorized actions **4,576**, versus sticky **4,573**; this is not a claim of improved decision accuracy.
- No hidden regime labels used in online decisions. [Source, visual report and audit](097/).
- Completed Turn 2 of 8. Next AETHER-098: deterministic diodic single-controller path.

## Phase rules

One hegemonic governing controller, deterministic best admissible action, diodic forward-only evidence, safe HOLD fallback, append-only failures. No distributed agreement or Byzantine branch inside Phase II. If the problem reaches independent witness/quorum/Byzantine requirements, **close and freeze the phase**, report the real completion percentage, and open the next phase. Eight completed turns independently close Phase II at AETHER-103.

**Next AETHER-097 — context contradiction and counterexample minimization.**

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
