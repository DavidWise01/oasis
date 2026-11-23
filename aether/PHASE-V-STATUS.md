# AETHER Phase V — Live Progress

**AETHER-120 integration accepted. PHASE V CLOSED: 8 / 8 turns = 100%.**

| Turn | Bound | Status | Completion |
|---|---|---|---:|
| 1 | 113 Verified ingress | **ACCEPTED** | **12.5%** |
| 2 | 114 Key rotation and expiry | **ACCEPTED** | **25%** |
| 3 | 115 Schedule freshness and delayed retirement | **ACCEPTED** | **37.5%** |
| 4 | 116 Temporal freshness | **ACCEPTED** | **50%** |
| 5 | 117 Anchor continuity and reacquisition | **ACCEPTED via 117B** | **62.5%** |
| 6 | 118 Risk-audit freshness | **ACCEPTED** | **75%** |
| 7 | 119 Unseen ingress stress | **ACCEPTED** | **87.5%** |
| 8 | 120 Integration freeze | **ACCEPTED — FROZEN** | **100%** |

## AETHER-120 — Phase V integration and closure

- **240 new synthetic episodes**, 40 seeds × six packet-delivery scenarios × 36 ticks, **8,640 single-controller decisions**.
- **1,920/1,920** checks passed across replay equivalence, immutable record chain, unique action per tick, packet-currency guard, independently calculated acceptance predicate, zero unsafe synthetic authorizations, bounded receipt accounting, and safe resumption.
- **5,717 ACT, 2,923 HOLD, 0 unsafe** on the bounded synthetic test.
- AETHER-118's policy was imported unchanged; pinned source SHA-256: `f7642313075830651348dd368496aa5f409236070466714b5010ab0fadc9ee4c`.
- Eight local historical experiment snapshots inventoried by SHA-256, including failed AETHER-117 alongside corrected AETHER-117B; earlier tests **were not comprehensively rerun**.
- Archive fingerprints refer to **local experiment snapshots** and do not establish byte identity with every historical GitHub file.
- Synthetic signer, source independence, timing, and protected counter assumptions remain unproven in a live system.
- [AETHER-120 source, manifest, inventory and interactive phase closure](120/) committed. Pages deployment live status unverified.
- **Phase V CLOSED at 100% (8/8).** New Phase VI must start from its own 0% tracker; do not change frozen Phase V evidence.

## AETHER-119 — Frozen packet-loss stress and bounded recovery

- **420 paired synthetic episodes**, 60 new seeds × seven scenarios × 36 inspections: 15,120 decisions per policy.
- Frozen AETHER-118 packet validator and ACT/HOLD selector imported unchanged, its SHA-256 pinned in the manifest.
- Cached evidence **535 unsafe authorizations** versus strict fresh evidence **0** across burst, long outage, reorder, intermittent, invalid signature, and counter-discontinuity cases.
- Clean scenario **2,159 / 2,159** safe ACT retained, no additional clean availability loss.
- **420 / 420** episode checks for acting at the first qualifying fresh *safe* packet after the test's recovery horizon; this is not proof of generic restoration latency.
- **5,040 / 5,040** replay, chain integrity, fail-closed, action-uniqueness, valid-source matching and zero-unsafe checks.
- Strict synthetic cost **382,065.6** versus cached **595,638.4**, contingent on this test's illustrative cost definition; strict holds more frequently while risk packets are unavailable.
- Simulated signature key, protected acquisition counters, and declared independent measurements remain **assumed trusted**.
- [AETHER-119 executable, acceptance manifest, results and interactive lab](119/) committed; GitHub Pages live deployment not independently checked.
- **Turn 7 accepted; Phase V 7/8 = 87.5%. Next AETHER-120 integration and phase freeze.**

## AETHER-118 — Fresh risk-audit packets under interruption

- **400 synthetic paired episodes**, 50 seeds × eight packet scenarios, 36 ticks each. 14,400 decisions/controller.
- Strict one-tick risk packet contract: valid HMAC/source/epoch, signed current tick, current protected acquisition counter, fresh monotonic packet ID, and declared independence.
- Cached risk comparator: **1,600 unsafe authorizations**; strict current-risk: **0**.
- Both policies retain **10,796 safe ACT** and 4 safe HOLD decisions; clean scenario 1,350 / 1,350 legitimate safe actions preserved.
- **4,000/4,000** deterministic replay, hash, one-action, fail-closed and current-packet checks passed.
- Illustrative cost: cached **985,364.8** vs strict **358,164.8**; savings 627,200 in these constructed scenarios, not a field estimate.
- The pretrusted risk signer, protected counter and independence declaration are assumptions, not derived authentication guarantees.
- [AETHER-118 source and interactive lab](118/) committed, with generated trace export available locally. Live Pages deployment is a separate unverified status.
- **Turn 6 completed; Phase V now 6/8 = 75%. Next AETHER-119: unseen ingress stress and recovery.**

## AETHER-117B — Corrected clock + fresh-risk acceptance

- Original AETHER-117 failure preserved: 40 unsafe authorizations in the delayed-anchor scenario.
- Fixed source tested across 40 seeds and 7 scenarios, 36 ticks per episode: 280 episodes per policy.
- The verified clock must be continuous and leased, **and** a separately authenticated, current independent risk-audit packet must satisfy the 2.5% upper-bound gate.
- Corrected fresh-risk policy: **0 unsafe ticks**, including 0/40 in the delayed-anchor cases.
- Clean scenario: **1,440/1,440** safe actions preserved. Verified restart: **40/40** recoveries; unverified restart remains closed.
- **3,360/3,360** deterministic replay, record chain, one-action and fail-closed checks passed.
- Total cost: weak 1,421,974.4; clock continuity 288,982.4; fresh-risk 305,121.6 units. Extra **16,139.2** is the audit-certification cost compared with clock-only; no universal economy claim.
- The separate risk signer and independent observations are **assumed trusted** in the synthetic evaluation.
- [AETHER-117B source, evidence and interactive lab](117b/). **Phase V advanced to 5/8 = 62.5%.**
- Next AETHER-118: interrupted risk-audit ingestion and freshness.

## AETHER-117 — Failed acceptance, preserved

- 40 synthetic seeds × seven anchor/counter scenarios × 36 ticks × two paired controllers.
- **2,240/2,240** deterministic checks passed; **verified restart recovery 40/40** and clean availability 1,440/1,440 were preserved.
- Weak verifier **2,600 unsafe authorizations**; continuity-aware verifier **40 unsafe authorizations**. The all-unsafe-eliminated acceptance gate **FAILED**.
- All 40 failures arise in the delayed-anchor case: a currently valid anchor can coincide with falsely clean risk observations during an actual hazard.
- Chronology is necessary but not sufficient for permission to ACT. The controller must require fresh risk evidence independent of the timing certificate.
- [Failed executable and report](117/) preserved append-only. **No credit: Phase V remains at 50%.**
- **Resolution:** AETHER-117B adds a current signed audit and passes its narrow synthetic gate; original failure retained.

## AETHER-116 — Clock lease and drift evidence

- **60 held-out synthetic seeds × six clock-fault scenarios × 32 inspection ticks × two paired controllers**, 360 episodes per controller.
- **2,880/2,880** deterministic replay, chain integrity, unique decision and fail-closed checks passed.
- Wall-clock comparator: **1,200 unsafe authorizations**; monotonic signed-anchor verifier: **0**.
- Clean rotation safe actions preserved: **1,499** under each policy.
- Total modeled cost: wall-clock **766,774.4** versus monotonic **288,982.4**, a reduction of **477,792** illustrative cost units.
- **All five gate conditions passed.** The source code, numerical summary, manifest and interactive HTML are archived at [116](116/).
- **Assumptions:** authentic signed time anchor, unrollbackable monotonic counter, drift bounded by 0.1 tick/tick, uncompromised HMAC fixture keys. This is not a field safety guarantee.
- **Next AETHER-117:** time-anchor freshness and counter continuity.

## AETHER-115 acceptance evidence

- 80 synthetic seeds × six credential-feed conditions × 28 ticks × two paired policies.
- **1,600 unsafe authorizations** under indefinite schedule caching versus **zero** under four-tick schedule leases.
- Clean rotation retained **1,759 safe ACT** decisions in both policies.
- Total illustrative cost: **917,548.8 cached**, **338,732.8 leased**; savings **578,816**.
- Availability tradeoff: safe HOLD decisions increased from **164 to 484**, including delayed notice and outage recovery.
- All five declared gates passed: no added unsafe authorization, strictly fewer unsafe authorizations, clean-rotation preservation, lower total cost and exact replay. The synthetic trace archive is preserved at [115](115/).
- **Important limits:** packet signing keys are fixture secrets; authentic schedule authority and local tick clock are assumed. Active-key compromise, falsified time, and independently verifying correlation remain unsolved.
- GitHub source committed; live Pages deployment remains unverified.
- **Next AETHER-116:** clock rollback, drift and expiry ambiguity, under one controller.

## AETHER-113 evidence

- 50 seeds × 7 scenarios × 24 ticks × 2 policies.
- Trusted controller: **0 unsafe authorizations** versus **2,000** for the naive policy.
- Clean action preservation **800/800 (100%)**.
- Four deterministic properties passed on all 700 cases: **2,800/2,800 checks**.
- Strong assumptions: toy trusted authentication key and truthful independence certification by the acquisition layer. Source authenticity is not proof of source independence.
- Reproducible [source, summaries and HTML](113/) are archived.
- AETHER-114 credential expiry and key rotation tested separately; see evidence below.
- **GitHub Pages source committed; live deployment not yet verified.**

## AETHER-114 acceptance evidence

- 60 evaluation seeds × seven credential scenarios × 24 ticks × two paired controllers = 840 cases.
- **3,360/3,360** deterministic replay, chain-integrity, fail-closed and admissibility checks.
- Keyring-only comparator: **720 unsafe authorizations** across three old-key misuse conditions.
- Epoch-bound controller: **0 unsafe authorizations** in these test conditions.
- Clean rotation preserved **960/960** legitimate safe actions.
- Trusted rotation schedule and retirement notification are **assumptions**; a compromised active key is not detected.
- Reproducible [source, numerical audits and interactive lab](114/) committed.
- AETHER-115 completed with the separate bounded-lease test recorded above.

The governing decision authority remains one deterministic ACT/HOLD controller. If witness agreement or Byzantine problems become necessary, close and freeze this phase at its current real percentage.

[Phase V charter](PHASE-V-113-120.md) · [Frozen Phase IV](PHASE-IV-STATUS.md)

`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
