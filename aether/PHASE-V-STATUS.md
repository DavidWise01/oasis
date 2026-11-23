# AETHER Phase V — Live Progress

**AETHER-117B accepted on the synthetic gate. 5 / 8 turns = 62.5%.**

| Turn | Bound | Status | Completion |
|---|---|---|---:|
| 1 | 113 Verified ingress | **ACCEPTED** | **12.5%** |
| 2 | 114 Key rotation and expiry | **ACCEPTED** | **25%** |
| 3 | 115 Schedule freshness and delayed retirement | **ACCEPTED** | **37.5%** |
| 4 | 116 Temporal freshness | **ACCEPTED** | **50%** |
| 5 | 117 Anchor continuity and reacquisition | **ACCEPTED via 117B** | **62.5%** |
| 6 | 118 Verification economy | Planned | 62.5% |
| 7 | 119 Unseen ingress stress | Planned | 62.5% |
| 8 | 120 Integration freeze | Planned | 62.5% |

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
