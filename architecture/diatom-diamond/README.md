# {{d}} — DIATOM / DIAMOND language v0.1

Derived, lossless carrier for the 42-address {{i}} isomorphic register. **KET and the frozen isomorphic kernel stay unchanged.**

## Geometry

Canonical four-port / three-coupler frame: `|.|.|.|`.

The four vertical bars name ordered vertex ports v0..v3; the three dots are explicit path couplers e01, e12, e23. A square/diamond projection can show a **derived fourth closure**, but this does not add a fourth serialized edge or claim a physical crystal lattice.

```
                v0
            .---' '---.
           v3         v1
            '---. .---'
                v2

stored: v0 -> v1 -> v2 -> v3   (4 vertices, 3 links)
```

## Preservation of {{i}}

The eight coordinate-distinct source lanes, indexed from zero:

- i1: `. : | ' z` (5)
- i2: `a b c d e` (5)
- i3: `f g h i j k` (6)
- i4: `l m n o p` (5)
- i5: `q r s t u v` (6)
- i6: `w x y 0 1` (5)
- i7: `2 4 6 8 0` (5)
- i8: `1 3 5 7 9` (5)

42 token IDs x 8 views = 336 view addresses; 42 token IDs x 8 source views x 8 destination views = 2,688 directed view-pair addresses. Both `i6:3` and `i7:4` display `0`, but are different tokens. Keep full addresses to preserve invertibility. The view operation is an identity-preserving relabeling until distinct view-transform rules are defined.

## Wire

Each cell is a single line:

```
{{d::v2>v6::|.|.|.|::4::i1:0,i6:3,i7:4,i8:0}}
{{d::v2>v6::|.|.|.|::1::i3:1,_,_,_}}
```

The integer after the frame is the occupied vertex count (1..4). Only the final cell may be partial. The remaining addresses are the padding sentinel `_`, which is not a valid {{i}} token or glyph `0`. The unique empty stream format is `{{d::v0>v0::|.|.|.|::0::_}}` (view tags vary). Cell order preserves source order.

## API and invariants

The JavaScript implementation exports `encode`, `decode`, `project`, `serialize`, `deserialize`, `glyphAt`, `ADDRESS_SPACE`, and `FRAME`. It rejects missing/out-of-range source addresses, mixed view headers, non-final partial cells, nonempty padding, and length mismatches. A structurally valid stream has `decode(deserialize(serialize(encode(stream)))) === stream` in token-coordinate order.

The `{{d}}` term is a symbolic shape analogy (diatom/diamond) — not a claim that atoms, photons, or Planck-scale mechanisms follow this language.
