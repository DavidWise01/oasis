# Four-Cortex VM Ladder v01

Status: **CANONICAL / SYMBOLIC SYSTEMS MODEL**

## Boundary primitive

```text
1x1 {{i}} 1x1
```

Interpretation:

- left `1x1` = source-local frame;
- `{{i}}` = invariant carrier;
- transform = JIT/runtime boundary re-expression operation;
- right `1x1` = destination-local frame.

A transform may change local representation, encoding, layout, instruction form, address representation, execution representation, or routing form. It must not change the carrier identity:

```text
{{i}}in = {{i}}out
```

## Cortex ladder

```text
[C1 IPv4]
    |
    | 1x1 {{i}} 1x1
    v
[C2 IPv6]
    |
    | 1x1 {{i}} 1x1
    v
[C3 quasi-q]
    |
    | 1x1 {{i}} 1x1
    v
[C4 quantum]
```

Canonical state models:

- C1 / IPv4 = classical bounded route state
- C2 / IPv6 = expanded classical route state
- C3 / quasi-q = candidate/permutation state
- C4 / quantum = coherent relational state

Each cortex may mutate its own local state. Only `{{i}}` is required to survive every VM boundary unchanged.

## Transform definition

```text
T := JIT/runtime boundary operation
     that re-expresses local state
     while preserving {{i}}
```

Formally:

```text
C1 --T1--> C2 --T2--> C3 --T3--> C4
```

with invariant extractor `I`:

```text
I(T(x)) = I(x)
```

## Benchmark status

The accompanying deterministic benchmark passed **11/11** checks:

- boundary shape
- four-cortex order
- identity preservation on ascent
- permitted local payload mutation
- cortex isolation
- boundary corruption detection
- frame invariance
- full round-trip identity preservation
- 100,000-transform identity stress
- 50,000 corruption-detection stress
- deterministic replay

This model is a symbolic/VM abstraction. It does not assert literal equivalence between IPv4, IPv6, quasi-q, and physical quantum implementations.
