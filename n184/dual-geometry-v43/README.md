# N184 v4.3 — Dual Geometry Freeze and Test

Add-only preservation of symbolic **box enclosure** versus **toroidal circulation**. No existing N184 files changed.

## Canonical four-brace enclosure

`{{{{ }}}}` holds the two parallel mappings and the unchanged phase operator `{{**--``--**}}`.

| Scale | Box | Evaluated | Toroid | Evaluated |
|---|---|---:|---|---:|
| Weak | `{{2x2}}^2` | 16 | `{{1x1}}^1` | 1 |
| Medium | `{{4x4}}^4` | 65536 | `{{3x3}}^3` | 729 |
| Strong | `{{6x6}}^6` | 2176782336 | `{{6x6}}^6` | 2176782336 |

Expression convention for this verification: `{{NxN}}^k` evaluates as `(N*N)**k`; symbolic packet glyphs are otherwise preserved literally.

## Phase-cross coordinates

- a = (x−2, y+3)
- b = (x−3, y+2)
- c = (x+2, y−3)
- d = (x+3, y−2)

Opposite pairs: a+c=0, b+d=0, hence sum(a,b,c,d)=0. The geometric term 'X' is a symbolic crossing, not an assertion of quantum tunneling.

## Test results

15 / 15 assertions passed in a Python deterministic local test on 2026-10-16.

- Both scale mappings match their numerical definitions (6)
- Strong equal; weak and medium distinct (3)
- Opposite point pairs and four-point zero sum (3)
- Frozen 60×40=2400; single conceptual gateway; literal four-brace delimiter (3)

This documents a mathematical model. It does **not** experimentally establish physical weak/medium/strong forces, toroidal matter structure, quantum transmission, or real atomic synthesis. Preserved base: the frozen 2,400 addresses, one in/out point, open-bottom enclosure, off-pillar protected VM.
