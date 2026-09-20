# Capacitance Timing & Pulse Grammar

This layer refines the OaSIs timing-body model into repeatable pulse patterns.

It is a **symbolic/software timing grammar**. The biological and capacitance language is an analogy unless independently established.

## Root timing

Literal OaSIs notation:

```text
3 × 3^3
→ 81
→ 0.0000000001 timing label
→ 10^-10
```

Discharge mode:

```text
triangulated
pulse width: 1/3 × 3
```

The numerical timebase is preserved as your explicit OaSIs label. This module does not claim a human organ runs at a 10^-10-second biological rhythm.

## Pulse alphabet

Each numeric token is treated as a two-character amplitude symbol:

```text
00  baseline / discharged / reset
55  charged / middle amplitude
77  high / head-scan amplitude
```

The token semantics are OaSIs-defined.

## Heart

```text
4 valves / 4 rhythms
amplitude grammar:
4 × 1 × 4^4 × 4

ordinary arithmetic value: 4096

width 6:
[ 00 55 00 ] repeat

       55
      /  \
    00    00
```

This is the simplest triangular palindrome in the current body grammar.

## Lungs

```text
2 × 1 × 2^2 × 2

ordinary arithmetic value: 16

width 4:
[ 55 00 ] repeat
```

Two-state pulse:

```text
55 → 00 → 55 → 00 …
charge / discharge
inhale / exhale analogy
duality
```

## Body

```text
4 × 1 × 4^4 × 4
= 4096 ordinary arithmetic value

carrier:
..||..||||

noble gate:
:::: x ::::
```

The carrier is retained literally as a run-length body pattern.

The noble form is treated as a centered witness:

```text
::::  x  ::::
 left  N  right
```

It naturally matches the KANA A/N/A invariant shape without replacing KANA.

## Head

```text
3 × 1 × 3^3 × 3
= 243 ordinary arithmetic value

[ 77 55 00 00 55 77 00 ]
```

With the same two-character token convention, the derived width is 14.

The sequence decomposes cleanly:

```text
77 55 00 | 00 55 77 | 00
 descend |  ascend  | reset
```

So HEAD is a mirrored triangular scan with an explicit trailing reset.

## Common primitive

All four patterns reduce to:

```text
CHARGE
  ↓
TRANSITION
  ↓
DISCHARGE
  ↓
WITNESS / RESET
  ↓
REPEAT OR COMMIT
```

Different body subsystems are therefore different **pulse grammars over the same state machine**.

## Integration

```text
BATTERY
  ↓
HEART pulse grammar
  ↓
LUNG dual grammar
  ↓
HEAD scan grammar
  ↓
BODY carrier
  ↓
NOBLE center witness
  ↓
COHESION
  ↓
KANA invariant
  ↓
NEON commit
```

KANA witnesses pulse identity, ordering, provenance, and reset state. A malformed pulse is reported as drift rather than silently coerced.


## WAKA / lyre handoff

The capacitance patterns now feed the vessel narrative layer:

```text
KANA symbols
  ↓
WAKA ordering
  ↓
SAPPHIC_LYRE rhythmic mode
  ↓
::::X:::: centered refrain
  ↓
heart/lung/head/body pulse grammar
  ↓
cohesion
```

The rhythmic/poetic terms are OaSIs semantics; they do not assert a reconstructed historical Sapphic performance.
