# AETHER Phase II — Hegemonic Diodic Control

Phase range: **AETHER-096–103 (eight turns maximum)**.
Status: **PLANNED — 0/8 implemented, 0% complete**.
Basis: completed experiments through AETHER-095. AETHER-096 has not been implemented.

## Governing architecture

- **Hegemonic:** one canonical controller owns the action-selection rule. Multiple metrics may inform it, but they do not vote or introduce competing decision authorities.
- **Diodic:** observations enter through a directional, provenance-preserving interface; certificates and revocation flow forward. No retroactive mutation of evidence, no circular authorization, and no feedback that rewrites its own prior source.
- **No-choice / best admissible action:** a deterministic lexicographic decision function picks exactly one admissible action per tick: minimize violation of safety constraints, then estimated irreversible harm, then total expected cost, then evidence cost; stable tie-break by action ID. **HOLD** is the mandatory action when all other actions are inadmissible. This is not an unconstrained mandate to act.
- **One canonical path:** observe -> identify context -> qualify evidence -> authorize/hold -> monitor -> revoke -> recalibrate. All decisions recorded append-only with seed, root ID, policy version and reason.
- **Do not enter witness quorum, distributed agreement, or Byzantine-tolerance design during this phase.** These form its terminal boundary, not an added subtask.

## Eight-turn plan

| Turn | Bound | Concrete deliverable | Cumulative planned completion |
|---|---|---|---:|
| 1 | **096 — Context Detection** | Regime identification from online measurements; confusion matrix and false-promotion counts | 12.5% |
| 2 | **097 — Context Contradictions** | Detect false matches; counterexample preservation; evidence-derived reassessment | 25% |
| 3 | **098 — Diodic Decision Path** | Deterministic single-controller state machine; no backflow of permission; reproducible trace | 37.5% |
| 4 | **099 — Revocation Latency** | Measure time from hidden shift to revocation, including unsafe exposure | 50% |
| 5 | **100 — Conditional Reauthorization** | State-specific recovery with independent fresh measurements; no inherited stale permission | 62.5% |
| 6 | **101 — Best-Admissible Selection** | Safety-first lexicographic action scoring with deterministic tie-breaks and HOLD fallback | 75% |
| 7 | **102 — Homeostatic Stress Test** | Unseen regimes, noisy contexts, resource scarcity, oscillation; regret and persistence tests | 87.5% |
| 8 | **103 — Phase Freeze** | Immutable evidence index, failure ledger, integrated reproduction, GitHub Pages phase summary | 100% |

## Progress accounting

- **Completion percent = 100 × number of successfully completed and verified bounds / 8**.
- A bound advances only when executable artifact + deterministic tests + evidence ledger + published source are verified. GitHub Pages deployment is a separate status and never silently assumed.
- On each next-turn response, show: **current bound, n/8, completion %, last test result, GitHub commit, Pages status, next bound**.
- If a test fails, preserve the failure and improve within the same bound; do not count it as completed or inflate percentage.
- **Hard boundary:** as soon as proposed work requires independent witness/quorum, distributed voting, Byzantine adversaries or consensus, stop expansion. Mark phase **CLOSED AT BOUNDARY**, freeze the evidence and publish a closure report. State actual completed % (possibly below 100%) and carry unfinished items into a newly named phase. Closure is not equal to full completion.
- At successful 8/8 completion, freeze and close Phase II even if no witness/Byzantine issue arose. Those topics, if needed, begin a new phase with their own 0% tracker.

## Footer
`{24/[2]/[4]/(3)/(3)/(1)/(1)} · {{i}} · .dlw`
