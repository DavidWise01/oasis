# {{i}} graded six-node chain v1.9c

Canonical user expression (exact lexemes and capitalization):

```text
{{i}} < {{so}} << {{more}} <<< {{Pp}} <<<< {{i}} <<<<< {{CcC}}
```

The additive parser recognizes **six ordered node occurrences** `i, so, more, Pp, i, CcC` and **five distinct links** of widths `1, 2, 3, 4, 5`. Together they contain 15 `<` signs. Two occurrences of `i` are at positions 0 and 4; their being the same *lexeme* does not by itself prove a physical or mathematical return-to-identity transformation.

The previous canonical arithmetic correction `{3x3}^{3} = 729` remains valid and **separate**. No mapping from the 729 arithmetic combinations to the chain is defined yet. `so`, `more`, `Pp`, `CcC`, and the five operator actions are preserved as user-authored literal tokens without inventing physical or numeric meanings. The `<` links are parsed as graded link lexemes, not comparison operators.

## Structural tests

`node architecture/diatom-diamond/iso-graded-chain-v1.9c.test.mjs` validates parser, canonical rendering, malformed input rejection, 42 coordinate-distinct `{{i}}` identities and all `42×8×8 = 2,688` source/target-view combinations. Every test route retains the exact lane, slot and displayed glyph, including distinct `i6:3` and `i7:4` both rendered as `0`. `i4:2` still renders `n`; the separate OBS44 registry's `00` also renders `n` but is not conflated with the original lane address.

The bridge currently **retains identity and labels**; it does not yet implement a physically meaningful transformation or substantive mathematical isomorphism because the relation to be preserved across `Pp`, `CcC`, and the link grades has not been specified. It is a strict grammar/route prototype, not a new quantum claim. Frozen KET, `{{i}}`, OBS44 and v0.7 floor source files remain unchanged. No mandatory witness/signature/checkpoint layer is introduced.

## Sources

- `iso-graded-chain-v1.9c.mjs` — parser and tagged identity routing
- `iso-graded-chain-v1.9c.test.mjs` — completeness and structural checks
- Original `diatom.mjs` and `I-DD-SPEC.md` remain the frozen/previous kernel references
