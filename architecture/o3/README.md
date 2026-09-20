# O3

**Canonical frozen Lean checkpoint.**

Status: **user-confirmed silent `0e`** on 2026-09-20.

Canonical source:

```text
lean/O3.lean
```

SHA-256:

```text
9ed23de7504fc284af95d4c39209a754d40886c0909d7d15c9121ff683e4d282
```

The previous filename `Oasis.GroundTruth.MitosisIso.00.lean` is retained only as provenance. `O3` is the canonical name.

## Proof

```text
{ /t/0\| + n | t+n || }

start 0 .
├── 0.1 ..
└── 0.2 ...

1 parent + 2 outputs = 3
3 × 6 + 2 verify = 20
```

The node labels remain symbolic strings. The transition glyph remains literal.

## Frozen invariants

```text
start/on-board       = true
ground-truth token   = .
mitosis outputs      = 2
total nodes          = 3
isomorph width       = 6
verify count         = 2
verify envelope      = 20
```

## Freeze rule

`O3` is immutable by release convention. New work must attach as a descendant rather than modifying the frozen source.