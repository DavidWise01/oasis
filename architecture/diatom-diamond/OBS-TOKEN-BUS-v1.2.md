# OASIS / KET :: OBS Token Bus v1.2

**Purpose:** Add a canonical bridge between the existing `{{i & dd}}` typed language and the nested `{{OBS}}` o/b/s core, while keeping previously frozen files unchanged.

**Original model:** `{{ specs {{ OBS {{ o 10^10 {{ b 100^100 {{ s 1000^1000 }} }} }} }} }}`. Source module: `obs-core-v1.1.mjs`. Dual floor source: `frozen/dual5-floor-v0.7/dual5.mjs`, pinned SHA-256 `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`.

## Encoding a token into one or more OBS cells

Each cell contains exactly three **canonical base-10 strings**:

```
{o:"0".."27", b:"0".."10^200-1", s:"0".."10^3000-1"}
```

- `o` is a *typed family*: `0..25` for `AaaA`..`ZzzZ`, `26` for canonical nonnegative decimal-number tokens, `27` for one Unicode punctuation/symbol code point.
- `b` is the **zero-based fragment sequence number within one token**; it resets to zero at the next token.
- `s` encodes 1–1245 bytes of UTF-8 via `256^byteLength + bigEndianByteValue`. This prefix preserves leading zero bytes and fragment length without out-of-band metadata. It is provably below `10^3000` for every allowed fragment.
- Tokens are represented as ordered runs of cells with `b=0,1,...` and constant `o`. A new `b=0` starts another token, even if both have the same kind. The empty stream is an empty list.
- The decoder rejects malformed length prefixes, out-of-bounds `o/b/s`, reserved `o` codes, missing fragments, noncanonical token forms, noncanonical decimal cell strings and stray properties. The reconstructed stream is re-encoded for a canonicality check.

**Finite bound:** each token can span at most `10^200` 1245-byte fragments in this particular version. Arbitrarily long practical strings are supported using multiple cells, but this does *not* provide an infinite-length token in one bounded physical packet. The possible number of finite packets is unbounded in the logical streaming model; implementation runtime memory remains finite.

## Inheritance from the immutable dual permutation floor

`CODE = UUDDLRLRBASS`, `PASSES = 5`, exactly **60 operations per rail**. Positive rail encodes `P^5(tokens)`; the negative rail encodes `P^-5(reverse(tokens))`, then applies the existing OBS complement `mirror(o,b,s)` to each cell and reverses the cell sequence. Recovery first removes the OBS mirror/reversal and then uses the inverse floor permutation. This requires **no new signed witnesses or checkpoint ledger**.

```
recover(positive) == reverse(recover(negative)) == original tokens
```

This is a deterministic *dual classical encoding*, not a proof of experimentally entangled qubits. The previously frozen floor's SHA-256 seal mechanism is historical and is not invoked by this token bridge, which imports only frozen tokenization and permutation operations.

## Read-only core dependencies

- `obs-core-v1.1.mjs` supplies `O/B/S`, exact mixed-radix encode/decode and OBS complement.
- `frozen/dual5-floor-v0.7/dual5.mjs` supplies canonical token families, `CODE`, `PASSES`, and the exact operator definitions. The freeze source hash is unchanged.
- This is an additive file. Neither the source registry nor the prior core is modified.

## Public exports

- `packTokens(tokens)` → flat list of OBS `{o,b,s}` coordinate records.
- `unpackTokens(cells)` → original typed tokens.
- `transform(tokens,inverse)` → five-pass floor permutation (no runtime witness required).
- `bindOBS(tokens)` → dual rail OBJ packet.
- `recoverOBS(packet)` → original typed tokens by consensus of both rail reconstructions.
- `addressView(token)` → original OBS mixed-radix cell addresses as exact decimal strings.
- `capacities()` → bounded coordinate facts.

## Run & visualize

```sh
node obs-token-bus-v1.2.test.mjs
python browser-smoke.py
```

The Three.js interactive viewer `obs-token-bus-threejs-v1.2.html` shows three nested obsidian-style faceted shells, two five-pass helical tracks, typed token spots, and a live coordinate inspector. If the browser cannot import Three.js from CDN, a tested interactive 2D canvas projection is provided. The 3D visualization is **schematic**, not scaled to actual `10^3210` volume and not hardware-validated. Obsidian is amorphous volcanic glass.

## Release results

Local Node 22 test run: **2,482 assertions passed**, **376 packets**, **4,852 typed fragments**, including a **9,000-decimal-digit** numeric token. Browser fallback: system Chromium smoke tests passed (JSON input, errors, selecting token, large-number chunking, scrubbing, visibility controls). CDN-loaded WebGL path is unverified in the offline environment.

The original v0.7 frozen floor remains byte-identical. No new witnesses, quorum, private signing keys, or checkpoint machinery are required.
