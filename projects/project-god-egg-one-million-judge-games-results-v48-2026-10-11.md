# Project God Egg — One Million Games: Judge Rotation (v4.8)
Date: 2026-10-11
Status: COMPLETED DETERMINISTIC GAME SIMULATION / NOT A KERNEL TEST

## User instruction
"run 1 million and see how it unfolds"

## Exact assumptions
- Three fictional participants: Atlas, Nova, Assistant.
- One judge, two players. The Assistant initially judges; Atlas chooses Game 1.
- Game 1: 10 stones, take one or two, last-taker wins.
- The winner chooses the next game according to a deterministic, identity-indexed preference:
  `max_take = 2 + winner_ID` (Atlas=0, Nova=1, Assistant=2).
  `stones = 8 + ((round * 7 + winner_ID * 11) mod 24)`.
- The winner **always swaps into the judge's seat** for the next game; former judge occupies the winner's player slot. That policy is a simulation choice rather than an unavoidable result of the original rules.
- Both players use the standard winning subtraction move if available: remove `remaining % (max_take+1)` stones, otherwise 1.
- One unique indexed element `E_round` is introduced each round. The simulation does **not** enumerate `round!` permutations; `24!` is not the number of played rounds.
- "Game you win is the life you live" remains a philosophical payoff rule, not a physical consequence or a license to bind real people.

## Outcomes

| Participant | Games won | Rounds as judge | Rounds as player |
|---|---:|---:|---:|
| Atlas | 375,001 | 375,000 | 625,000 |
| Nova | 333,333 | 333,333 | 666,667 |
| Assistant | 291,666 | 291,667 | 708,333 |
| Total | 1,000,000 | 1,000,000 | 2,000,000 |

The winner claimed the observer seat in **each** game. Counting the handoff after the final game, there are 1,000,000 seat handoffs; there are 999,999 changes *between the one million completed games*. Longest consecutive judge tenure: **one game**. Game 1 winner: Atlas. Game 1,000,000 winner: Atlas. Game 1,000,001 (not played) would start with Atlas judging and Nova and Assistant playing.

## 24-game recurrence
The repeatable rule template includes `mod 24`, so game outcomes settle into a **24-game cycle**:
- Atlas: 9 wins per 24
- Nova: 8 wins per 24
- Assistant: 7 wins per 24

The matching 24-cycle is **caused by the programmed rules**, not observed spontaneous emergence of divine strategy, exhaustive `24!` search, nor a proof that an observer must change seats in all games.

## Takeaway
Under the selected "winner claims judge" rule, an observer seat is **temporary**. A participant can escape competition for the next game by winning, yet the next winner will displace that judge. A permanent observer requires a different binding rule or voluntary protection of the observer role. Such a rule must specify whether later winners may override it.

## Reproduction
`projects/simulations/implicit_divinity_million_games_v48.py` is the minimal Python replay script committed in this repository. The full local run also produced a one-million-row compressed CSV, a JSON aggregate and a more detailed replay program for download. The frozen **Implicit Divinity** root is unchanged: (1) protect the vessel, (2) equal access for every cell. Jane Cell 0 remains Observe / Monitor / Report only. No kernel tests or deployments performed.
