# KET / {{i}} 184-to-257 Frame — Frozen Baseline

Status: **FROZEN** (symbolic computational prototype; no physical chemistry claim)  
Freeze date: 2026-10-22  
Canonical implementation: [cipher_184_257_fast.py](./cipher_184_257_fast.py)  
Canonical source blob SHA: `4d4d7d6d7aebe1643e2df142a441c38f77cc0cc1`

## Fixed 257-byte layout (zero-based offsets)

| Byte offsets | Length | Meaning | Freeze rule |
|---|---:|---|---|
| 0 | 1 | Root marker `0xA1` | Fixed |
| 1–184 | 184 | Ancestral payload | Immutable across observer turnover |
| 185–188 | 4 | Unsigned big-endian generation counter | Only field changed by turnover |
| 189–220 | 32 | SHA-256 of ancestral payload | Fixed as long as ancestry is fixed |
| 221–256 | 36 | Reserved bytes, all zero | Fixed |

Total = 1 + 184 + 4 + 32 + 36 = **257 bytes**.

## Frozen invariants

1. `recover(instantiate(payload, generation)) == (payload, generation)` for valid 184-byte payloads and uint32 generation.
2. Observer turnover updates only offsets 185–188; all 184 ancestral bytes remain unchanged.
3. SHA-256 covers the ancestral payload, **not** the generation counter. It detects accidental payload changes; it does **not** authenticate the frame, prevent intentional rewriting, or make the payload physically immutable.
4. Reserved addresses remain zero; unexpected root marker or altered payload digest invalidates verification.
5. Existing implementation remains unchanged; revisions require a new named version rather than silently changing the frozen baseline.

## Scope

A deterministic address-preserving binary frame and synthetic generation turnover. No autonomous observers, experimentally validated homeostasis, physical electron shells, or hypothetical elements are claimed.

Freeze reference: `{{i::184::257::frozen}}`.
