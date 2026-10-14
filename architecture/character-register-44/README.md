# KET Symbol Register v0.1 — 44 addresses

**Additive** symbolic address table. Frozen KET kernel and other 208-state/366-state registries are untouched. Mapping follows the user's sequence, with its otherwise unnumbered `n` assigned the center address `0` as accepted in conversation.

| Address | Symbol range |
|---|---|
| `0` | `n` — center |
| `1..13` | `a..m` |
| `14..23` | `o..x` |
| `24..33` | `y z 1 2 3 4 5 6 7 8` |
| `34..43` | `9 > \| : " ^ ( - + .0x` |

There are exactly **26 lowercase letters + 9 standalone digits (1–9) + 9 special tokens = 44 distinct symbols**. The center label `0` is an integer *address*, not a standalone digit token. `.0x` is one custom three-character token, not a hex literal or three independent symbols. There is no independently addressable period (`.`) or digit zero (`0`).

## Usage

```sh
node register.mjs
node test_register.mjs
```

```js
import {addressOf, tokenAt, encode, decode, tokenize} from './register.mjs';
addressOf('n');           // 0
tokenAt(43);              // '.0x'
encode(['h','o','n','e','y']); // [8,14,0,5,24]
decode([8,14,0,5,24]);    // ['h','o','n','e','y']
tokenize('honey.0x');     // ['h','o','n','e','y','.0x']
```

## Limits

This tests bijectivity, boundary conditions, round trips, and lexical handling. It does **not** independently prove correspondence with physical elements, time, life, network routing, or the larger KET governance model. "44" counts addressable symbols, not 44 extra KET kernel tracks. No existing file is replaced.
