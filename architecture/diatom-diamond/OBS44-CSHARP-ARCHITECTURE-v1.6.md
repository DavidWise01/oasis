# OBS44 additive C# architecture

Canonical user mapping is 44 address slots: 00..43. Ordered registry: `n` at 00; `a..m` at 01..13; `o..x` at 14..23; `y,z,1..8` at 24..33; `9,>,|,:,",^,(,-,+,.0x` at 34..43. No repeated glyph keys. `.0x` is a single terminal token, not a number, a hexadecimal literal, or a split sequence.

## Compatibility contract

The prior frozen floor's validator only accepts `AaaA..ZzzZ`, canonical decimal strings, and single Unicode special scalars. Plain `n` and `.0x` are not valid input to that validator. OBS44 therefore encodes addresses as canonical decimal strings `"0".."43"` at the boundary; the zero-center display `00` becomes `"0"` on the floor wire. The typed envelope `OBS44/address-v1.6` disambiguates surface glyphs from preexisting numeric values.

This encoding preserves the original code's exact permutation, inverse and OBS packing with no changes to historical source files. However, the OBS layer's `o=26` reflects the **numeric carrier kind**, not the mapped surface class. A future dedicated address-token carrier could reserve a different `o` code, but that would be a new version and should not be silently introduced.

## Direct examples

| OBS44 display address | Surface glyph | v0.7 floor code | Packed OBS `o` | `s` payload for first and only chunk |
|---|---|---|---|---|
| `00` | `n` | `"0"` | 26 | 304 |
| `01` | `a` | `"1"` | 26 | 305 |
| `34` | `9` | `"34"` | 26 | 78644 (`65536 + 0x3334`) |
| `43` | `.0x` | `"43"` | 26 | `65536 + 0x3433 = 78899` |

The script and oracle are authoritative for numerical payload values. The `s` value is `256^length + bigEndian(UTF8(canonicalDecimalCode))`.

## Responsibilities

- `src/ObsAddress44.cs` — table, strict address lookup, versioned OBS44 protocol envelope, bridge to the immutable `ObsKernel` code.
- `src/ObsKernel.cs` — existing .NET reference of the frozen dual permutation and OBS coordinate transformations, copied without alteration from the previous local reference project.
- `src/ObsStreaming.cs` — existing bounded C# channel processing code, copied without alteration.
- `oracle/obs44-test.mjs` — independent test against original OBS JavaScript source; generates parity vectors in `results/`.

No new signatures, witnesses, mining, quantum processing, or encryption layers.