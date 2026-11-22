# AETHER Phase II — Live Progress

**Completed: 6 / 8 turns · 75%**  
**Current status: AETHER-102 failed per-regime generalization; AETHER-102B next.

| Turn | Bound | State | Cumulative completion |
|---|---|---|---:|
| 1 | 096 Context detection | **Accepted via 096B** | **12.5%** |
| 2 | 097 Context contradictions | **Accepted** | **25%** |
| 3 | 098 Diodic decision path | **Accepted** | **37.5%** |
| 4 | 099 Revocation latency | **Accepted via 099B** | **50%** |
| 5 | 100 Conditional reauthorization | **Accepted via 100B** | **62.5%** |
| 6 | 101 Best-admissible action | **Accepted** | **75%** |
| 7 | 102 Homeostatic stress | **TESTED — FAILED; revise as 102B** | **75%** |
| 8 | 103 Freeze and closure | Not started | 75% |

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

## AETHER-098 completion evidence

- Deterministic controller across 80 independent synthetic seeds × 3 regimes × 96 ticks = **23,040 decisions**.
- **240/240** deterministic replay comparisons passed.
- **240/240** changed-future causal-prefix comparisons passed; earlier actions and hashes unchanged.
- **240/240** append-chain recomputation tests passed.
- **240/240** unused-sentinel perturbation tests passed.
- Nontrivial authorization was observed: **15,544 ACT** and **7,496 HOLD** decisions.
- **384** context revocations were recorded.
- A preliminary over-conservative confidence bound caused all-HOLD; corrected before the accepted run.
- [AETHER-098 source and report](098/) and outputs published. Pages live deployment is a separate check.
- The observed risk bound is retrospective; synthetic causal replay is not a production safety guarantee.

**Next: AETHER-099 — revocation latency and unsafe exposure.**

## AETHER-099 failed-bound evidence

- 80 paired seeds in each of abrupt, gradual and decoy proxy-shift environments, 100 ticks each.
- Sensor-assisted policy cut unsafe authorized inspections **44 → 1**, but increased safe holds **942 → 4,827**.
- Total illustrative cost rose **160,545 → 173,105**, an increase of **12,560**.
- Acceptance gate (≥20% fewer unsafe authorizations, non-increasing cost, ≤5% added safe holds): safety criterion passed, cost and safe-hold criteria **failed**.
- The decoy context is a preserved counterexample; sensor signals can change while action risk stays safe.
- The rolling-only controller retains governing authority. [AETHER-099 failed experiment](099/).
- **Completion stays 3 / 8 = 37.5%.** AETHER-099B will use new development and holdout seeds.

## AETHER-099B accepted correction — Turn 4

- Development on **40 distinct seeds per regime**; 18 candidate alarm gates; frozen choice: audit error count ≥2, observed proxy ≥2.0, no extra cooldown.
- Independent final evaluation on **80 new seeds per regime**, 24,000 ticks/controller across abrupt, gradual, decoy conditions.
- Unsafe authorizations: rolling **42**, conditional **3** (92.86% reduction).
- Additional safe HOLDs **333**, 1.6584% of safe inspections (≤5% acceptance gate).
- Modeled cost: rolling **159,600.0**, conditional **157,718.4**, savings **1,881.6**.
- Continuous sensor comparator remains expensive, **172,575.0**.
- The decoy regime alone still favors rolling-only; aggregate acceptance is not universal dominance.
- [AETHER-099B reproducible source and report](099b/).
- **Phase II now 4/8 = 50%. Next AETHER-100 fresh-evidence reauthorization.**

## AETHER-100 failed-bound evidence

- Fresh-evidence policy selection tested 40 development seeds per regime; **neither candidate eligible**, so no promotion.
- 80 unseen holdout seeds each for abrupt recovery, repeated hazard and sensor-only decoy.
- Unsafe authorizations equal: stale 4; fresh3 4; fresh5 4.
- Safe holds: **stale 1,315; fresh3 2,559; fresh5 2,572**.
- Average recovery delays: **2.677 / 6.204 / 6.210 ticks**.
- Total costs: **166,062.5 / 169,502.5 / 169,550.0**.
- Completion stays **4/8 = 50%**; fresh evidence has not yet met the utility gate.
- [AETHER-100 executable, negative result, and dashboard](100/).
- Next **AETHER-100B**: conditionally earned, non-resetting fresh certificates; independent development and evaluation.

## AETHER-100B accepted completion evidence

- Initial AETHER-100 was a failed performance test: fresh3 and fresh5 caused excessive recovery delay and safe abstention. It remains archived at [100](100/).
- AETHER-100B permits post-revocation evidence to accumulate without repeated reset during one continuing suspension.
- Fresh2 was chosen on **40 independent development seeds per scenario (100301–100340)** before scoring **80 new holdout seeds (100501–100580)** in each of three scenario families.
- On 240 paired holdout cases, unsafe authorizations were **12 for both controllers**; safe holds **1,354 → 739**.
- Mean recovery delay **3.041 → 1.106 inspections** and total cost **167,045 → 165,172.5**, a **1,872.5** saving.
- Additional ordinary wrong outcomes **8,078 → 8,352**, because more safe-period actions were authorized. Do not claim error-free superiority.
- Four predeclared safety, safe-hold, cost, recovery-delay gates all passed. **Turn 5 completed, 62.5% Phase II.**
- [AETHER-100B executable source, data, and Pages-ready report](100b/). Live deployment remains separately unverified.
- **Next AETHER-101: Best-Admissible Action Selection.**

## AETHER-101 completion evidence

- 80 seeds × 3 environments × 96 inspections = **23,040** controller decisions.
- **Five test categories × 240 seeded episodes = 1,200/1,200 passes**: deterministic replay, future prefix, action ordering, hash integrity and exact argmin.
- One safety-admissibility bound for both DIRECT and GUARDED. Otherwise HOLD.
- Action counts: DIRECT **16,304**, GUARDED **276**, HOLD **6,460**.
- Wrong authorized outcomes **8,733 → 8,317**, total cost **184,616 → 180,621.6** (3,994.4 savings).
- Unsafe authorized ticks **137 → 137**, unchanged.
- Guarded-action risk reduction of 45% is a **synthetic assumption**; results are not a field guarantee.
- [Reproducible experiment](101/) and Pages-ready report committed; live deployment unverified.
- **Next: AETHER-102**, unseen-dynamics homeostatic stress. Closing phase only after 103 or its independent-witness/Byzantine boundary.

## AETHER-102 unseen-dynamics counterexample

- 60 new synthetic seeds in each of five regimes, 300 episodes × 96 ticks = **28,800 decisions** per policy.
- Frozen AETHER-101 selector imported without changes; 300/300 replay, prefix-repeat, hash-integrity and admissibility checks in each category.
- Aggregate selector cost **238,832.2**, versus direct-only baseline **244,783.0**, an improvement of **5,950.8** units.
- Unsafe authorized ticks remained **236** under both policies.
- **Critical guard-degradation regression:** baseline **49,593.5**, selector **50,036.7** = **+443.2**. The benefit of the guarded action was not observable to the controller.
- Prespecified acceptance required no *per-regime* cost regression: **FAILED**.
- **Completion holds at 6/8 = 75%.** [AETHER-102 failed test](102/).
- **Next AETHER-102B:** observation-based guard-effectiveness gate, frozen then tested on untouched seeds.

## Phase rules

One hegemonic governing controller, deterministic best admissible action, diodic forward-only evidence, safe HOLD fallback, append-only failures. No distributed agreement or Byzantine branch inside Phase II. If the problem reaches independent witness/quorum/Byzantine requirements, **close and freeze the phase**, report the real completion percentage, and open the next phase. Eight completed turns independently close Phase II at AETHER-103.

**Next AETHER-097 — context contradiction and counterexample minimization.**

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
