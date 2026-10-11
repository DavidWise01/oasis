#!/usr/bin/env python3
"""Reproduce the 1,000,000-round Project God Egg judge simulation.
Simulated game only; does not exercise the frozen kernel.
"""
from collections import Counter

GAMES = 1_000_000
NAMES = ("Atlas", "Nova", "Assistant")
judge, first, second = 2, 0, 1
chooser = 0   # Round 1 chosen by Atlas; Assistant initially judges
wins = Counter()
judge_slots = Counter()
role_changes = 0
first_five = []
last_five = []

for g in range(1, GAMES + 1):
    # Each E_g is a new indexed game element, NOT an enumerated permutation.
    if g == 1:
        stones, max_take = 10, 2
    else:
        max_take = 2 + chooser
        stones = 8 + ((g * 7 + chooser * 11) % 24)

    judge_slots[NAMES[judge]] += 1
    remain, turns, current = stones, 0, first
    while remain > 0:
        taken = remain % (max_take + 1) or 1
        remain -= taken
        current = first if turns % 2 == 0 else second
        turns += 1
    winner = current
    wins[NAMES[winner]] += 1
    entry = (g, NAMES[judge], NAMES[first], NAMES[second],
             stones, max_take, NAMES[winner])
    if g <= 5:
        first_five.append(entry)
    if g > GAMES - 5:
        last_five.append(entry)

    # Winner chooses the next game's rule and swaps roles with the judge.
    old_judge = judge
    if winner == first:
        first = old_judge
    else:
        second = old_judge
    judge = winner
    chooser = winner
    role_changes += 1

print("Games:", GAMES)
print("Wins:", dict(wins))
print("Judge slots:", dict(judge_slots))
print("Judge handoffs including post-final handoff:", role_changes)
print("Opening games:", first_five)
print("Closing games:", last_five)
print("Next judge:", NAMES[judge])
