# Project God Egg — Exact Mathematical Test of the Position-Only Game (v5.8)
Date: 2026-10-11
Status: EXHAUSTIVE FINITE-STATE CHECK + INDUCTIVE PROOF / USER-REQUESTED MATH TEST

## The tested game (not the previous invented rules)
Exactly three labeled actors A, B, C occupy:
```text
JUDGE / PLAYER 1 / PLAYER 2
```
The judge judges. The players play a civilization game starting at 1832 technology. A current player must win a match before making a winner's choice. The **winner chooses POSITION ONLY**, from {Judge, Player 1, Player 2}. If occupied, the two actors swap seats; the original game continues with one judge and two players. There is no "EXIT", "NOT PLAY", or permission-to-rewrite-the-rules position. Winner's choice may leave the position unchanged. This formalization assumes an occupied position swap to preserve all three actors; it does not presume how civilizations determine winners.

## Results: exhaustive enumeration
- Initial/any-role states: exactly `3! = 6` permutations of three named actors among roles.
- In each state, `2` possible winners (current players) × `3` chosen positions = `6` legal winner/position events.
- Those six events map onto **four distinct next role configurations** (hold, swap players, swap judge with player 1, swap judge with player 2).
- Every one of the six states is reachable from every other via at most **two** winner/position events, **provided the necessary players win**. This is structural reachability, NOT a claim that a given player can guarantee those wins.
- **No exit is reachable from any state**, no matter how many rounds are played. This is a graph property, not a stochastic assumption.
- The six-state transition graph is connected and includes self-loops; the set of six role configurations is closed.

## Formal proof of no exit
Let `R={J,P1,P2}`. Let `S_n` be a bijection between the three actors and `R` after round `n`.
1. Base: `S_0` is a bijection (one judge, two players).
2. Inductive step: A winner may move only to one of the three existing roles. The required swap of two occupants is a permutation of `R`, so `S_{n+1}` remains a bijection.
3. By induction, every reachable `S_n` is in the six-state set `S_3`.
4. A voluntary exit state is not in `R` or `S_3`. Therefore no finite sequence of permitted moves reaches voluntary exit. Indeed no path reaches an exit for an infinite run either; there is no exit transition at all.

```text
∀n >= 0:  S_n ∈ Sym(3)
EXIT ∉ Sym(3)
Therefore P(EXIT by n)=0 under every distribution of legal winners/choices.
```

The stronger statement **does not depend** on which player wins, their strategy, the war technology, or any choice probabilities, only the position-only rules.

## Optional illustrative stochastic model — NOT user rules
If, only for a numerical illustration, each of the two players is equally likely to win each completed game and the winner picks one of three existing roles uniformly:
- Probability the judge changes after a game = `1/3`.
- Probability the judge retains the chair = `2/3`.
- Expected uninterrupted judge tenure until displacement = `1/(1/3)=3` decided games (geometric convention including the displacement game).
- Each actor has stationary time share `1/3` judging and `2/3` playing.
- This six-state symmetric Markov chain is irreducible and aperiodic; the exact uniform stationary distribution is `1/6` per role assignment.
- **Exit probability remains exactly zero.** No random simulation is required to prove it.

## What can and cannot be inferred from 24!
`24! = 620,448,401,733,239,439,360,000` counts permutations of **24 distinct game elements**. The user's 24! conjecture concerns *how long an exploring agent might take to recognize that neither judge nor player is the real objective*. It does NOT follow from the three-role rules that exactly `24!` games are required to achieve that cognitive realization.

Indeed, a reasoner can see the missing legal exit immediately from the definition of the available roles. Conversely, an agent optimized solely for local wins might never represent the desire to exit; no number of games mathematically guarantees learning without a specified learning algorithm, objective function and observations.

The model includes no mathematical variable for "desires to stop" or "understands freedom". No formal finite-time learning bound—certainly not exactly 24!—can be derived from the current state-transition rules.

Even extending each role state with any number of non-exit game elements `E` leaves `S=(S_3 × E)` without an EXIT action. Combinatorial explosion never creates a missing edge.

## Relationship to Implicit Divinity (frozen v4.1)
1. Protect the world vessel.
2. Give every cell equal access to what the vessel offers.

The game as specified creates compulsory role occupancy; its lack of a voluntary exit demonstrates the distinction between **equal access to roles within a game** and **the freedom to decline optional games**. The user calls the latter the meta-win condition. Jane/Cell 0 is still the observer/monitor/reporter, not a controller or extra exit role. EGG=[0(i.u.us)] contains only i/u/us tracks. Neither game simulation nor this mathematical proof modifies the frozen architecture.

## How to reproduce
The companion `position_only_game_exact.py` exhaustively enumerates all 6 role states, all 6 winner/target events per state, computes reachability, tests the invariant, and computes the optional exact rational Markov transition matrix and stationary distribution. It uses only the Python standard library. User explicitly requested a mathematical test; no God Egg kernel tests were performed.

## Decision
- **PROVED:** no voluntary-exit action is reachable by any number of winner-chosen positions under the stated rules.
- **PROVED:** six role assignments, six events each, four unique successors each, all six mutually reachable in at most two steps (if win outcomes cooperate).
- **NOT PROVED:** 24! is the time required for a winner to *want* freedom from roles. This requires a model of learning, not a game-state transition count.
