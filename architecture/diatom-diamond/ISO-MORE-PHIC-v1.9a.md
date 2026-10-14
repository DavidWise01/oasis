# OASIS / KET — `{{i}}` ISO::MORE::PHIC overlay v1.9a

**Historical source expression (superseded by the v1.9b correction):**

```text
{{iso:: more :: phic :: or {{3.3}}^{-{+{ positron -e+ gravitron }+}-} }}
```

This document corrects an overly narrow description of `{{i}}` as merely a 42-address lookup table. The 42 coordinate-distinct source addresses and eight existing views are an *implementation substrate* for an **isomorphic transformation language**, not the whole meaning of `{{i}}`.

## v1.9b — corrected arithmetic notation (2026-10-13)

**Latest user-defined arithmetic form:** `{3x3}^{3}`, where a dot `.` written between scalar numerals is multiplication `×`, **not a decimal separator**.

```text
{{iso:: more :: phic :: or {3x3}^{3}}}
```

Arithmetic evaluation under ordinary integer multiplication/exponentiation:
```text
{3x3}^{3} = (3 × 3)^3 = 9^3 = 729
```

This **replaces the earlier ambiguous numeric interpretation of `{{3.3}}`**. The separate older symbol string `-{+{ positron -e+ gravitron }+}-` is preserved below for provenance, but its placement and action relative to the corrected exponent are **not defined** by this arithmetic correction. In particular, do not treat it as the exponent `3`, and do not silently exponentiate by that shell.

### Active numeric parse
```text
Power
├── base: Multiply(3, 3)
└── exponent: Integer(3)
value: 729
```

## Historical literal structure (superseded for arithmetic, retained as provenance)

| Source form | Status | Interpretation for software |
|---|---|---|
| `iso:: more :: phic` | canonical user spelling | Names the isomorphic/morphological correspondence layer; do not silently rename or collapse these three operands. |
| `or` | literal alternative connector | Do not assume Boolean XOR, arithmetic disjunction, or substitution until semantics are specified. |
| `{{3.3}}` | literal scalar-expression token | Preserve its exact decimal spelling; do not presume (3\times3), a version number, or an empirically measured constant. |
| `^{-{+{ ... }+}-}` | literal superscript signed enclosure | Treat as an unevaluated operator tree, retaining both outer minus signs and both inner plus signs. |
| `positron -e+ gravitron` | user-authored symbolic sequence | Retain the exact `-e+` connector and spelling `gravitron`; **no automatic replacement with `graviton`** or numerical charge operation. |

## Explicit symbolic parse

```text
ISO_MORE_PHIC
├─ term[0] = iso
├─ term[1] = more
├─ term[2] = phic
├─ alternative = or
└─ expression
   ├─ base = {{3.3}}
   └─ superscript = -{ +{ positron -e+ gravitron }+ }-
```

This is a *syntax/representation* parse, not a proven physical formula.

## Invariants to test independently

1. Isomorphic transformations must specify the relation they preserve (at minimum, a reversible map of each source identity and its lane/slot coordinates), and an inverse should restore the original complete address.
2. Distinct addresses sharing a glyph must remain distinct. E.g. `i6:3` and `i7:4` both display `0`, but are separate.
3. The original 42×8 source registry (336 view addresses; 2,688 directed source-view/destination-view combinations), OBS44's separate `00=n` registry, frozen KET, and frozen dual-floor v0.7 remain unchanged.
4. The revised integer expression `{3x3}^{3}` round-trips exactly and evaluates to `729`; the separately recorded signed positron/gravitron shell round-trips verbatim without a presumed numerical effect.
5. `3x3` is ordinary multiplication and superscript `3` is ordinary exponentiation; the roles of `or`, `-e+`, and `gravitron` remain explicitly unspecified pending the canonical rules. Nothing here makes an ungrounded mapping a verified fact.

## Physics boundary

A positron is the electron's positively charged antiparticle. `Gravitron` is **not** a standardized, experimentally observed fundamental particle; the graviton, spelled differently, is a hypothetical quantum of the gravitational field. This proposed notation alone is not evidence of coupling, a mass/charge transformation, entanglement, or an absence of propagation delays.

## Implementation note

Attach as a namespaced symbolic AST **above** the frozen `{{i}}` registry. Optimize the reversible address mappings and physical network transport independently. Do not mutate the frozen floor and do not reintroduce mandatory witness/signature/checkpoint machinery.
