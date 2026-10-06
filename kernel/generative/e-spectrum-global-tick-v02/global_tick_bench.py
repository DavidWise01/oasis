from dataclasses import dataclass
from time import perf_counter

@dataclass(slots=True)
class Cell:
    tick: int = 0
    active: bool = True

def cycle(cells):
    for c in cells:
        if c.active:
            c.tick += 1

def benchmark(n, cycles):
    cells = [Cell() for _ in range(n)]
    start = perf_counter()
    for _ in range(cycles):
        cycle(cells)
    elapsed = perf_counter() - start
    updates = n * cycles
    assert all(c.tick == cycles for c in cells)
    return {
        "cells": n,
        "cycles": cycles,
        "updates": updates,
        "seconds": elapsed,
        "updates_per_second": updates / elapsed if elapsed else float("inf"),
    }

def invariant_tests():
    cells = [Cell(), Cell(active=False), Cell()]
    before = [(c.tick, c.active) for c in cells]
    cycle(cells)
    after = [(c.tick, c.active) for c in cells]
    assert before == [(0, True), (0, False), (0, True)]
    assert after == [(1, True), (0, False), (1, True)]

    cells = [Cell() for _ in range(1024)]
    for _ in range(100):
        cycle(cells)
    assert all(c.tick == 100 for c in cells)

if __name__ == "__main__":
    invariant_tests()
    print("0e / GLOBAL TICK INVARIANTS PASS")
    for n, cycles in [(1_000, 1_000), (10_000, 200), (100_000, 20), (1_000_000, 2)]:
        print(benchmark(n, cycles))
