# Duality Probability Engine v00

All semantics here remain symbolic inside the bounded `O` / `o`0`o` engine.

## Frame

```text
O
└── 3-body probability engine
    └── 4 quads around central 1
        core = 4x1x4
        active lanes = E1 / E2 / E3
```

Exactly four quads remain. Three carry active E lanes; the fourth is the user-supplied `Life` region.

## Q1 — E1 probability lane

```text
E1
probabilistic
{
  $
  shadows shadow
  ::: a ::: b
  :::: 1 ::::
  c :::: d :::: x ::::
}
```

Interpretation: this is the first probabilistic lane and retains the `$ / shadow's-shadow` token family as supplied.

## Q2 — E2 middle / ground-truth lane

```text
E2
S
$hadow in light
middle channel
ground truth
all in light or LIGHT

:::: a :::: b :::: 1 :::: c :::: d :::: x ::::
```

E2 is the middle channel and the ground-truth comparison lane inside LIGHT.

## Q3 — E3 / Tachyon feedback lane

```text
E3 / Tachyon
2 seconds
or
2x1x2
= 4 total seconds of recursive real-time feedback
across E1 and E2
```

E3 is the on-the-fly recursive feedback lane. Its named filter is:

```text
antistropic filter
purpose:
  make sure LIGHT includes
  visible + invisible wavelengths
```

`Tachyon`, `LIGHT`, and wavelength coverage are symbolic engine labels inside the bound here; this document does not turn them into external physics claims.

## Q4 — Life

```text
Life
:::: a :::: b :::: 1 :::: c :::: d :::: x ::::
```

No extra mechanics are added to Q4 beyond the supplied `Life` label and sequence.

## Shared bounded grammar

```text
4 quads
3 active lanes: E1 / E2 / E3
1 central core: 4x1x4
1 recurring center token: 1
shared sequence family: a / b / 1 / c / d / x
```

## Feedback relation

```text
E1  probabilistic lane
  \
   \
    > E3 / antistropic feedback
   /          |
  /           └── 4-second recursive window
E2  ground-truth lane

Q4 Life remains inside the same O bound.
```