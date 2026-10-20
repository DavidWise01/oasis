# GG-ZERO · RGB Diffusion 11 — distance experiment

[**Play extended diffusion on GitHub Pages**](https://davidwise01.github.io/oasis/apps/game-gear-zero/) · [Download compiled 16 KiB cartridge](./dist/rgb-diffusion-11.gg) · [Z80 source](./games/rgb-diffusion-11.js) · [I-13 source intent](./examples/i13-rgb-diffusion-11.i13)

## Symbolic mapping / assumed scope

User notation, preserved verbatim:

```text
. > 2^3 = 8 = 11 {2/2|{4|/2/2
```

The project already defines dot `.` as an eight-state carrier, `2³` being the RGB sign pairs `R -+`, `G -+`, `B -+`. The precise meaning of the new trailing expression was not previously established. **This build's provisional operational interpretation** is:

- `.` = a seed/source cell;
- `2³ = 8` = all three-bit RGB masks 0..7;
- `11` = the first **measured hop checkpoint**, *not* an arithmetic identity `8 = 11`;
- `{2/2 | 4 | 2/2}` = directional pairing around the four-port von Neumann (N,S,E,W) neighborhood; pairing is a symbolic overlay, not another proven law.

This experiment tests that mapping without freezing it as canonical KET/I13 grammar. There is **no physical quantum diffusion** in this release.

## From 192 to 320 cells

The new game expands from 16 × 12 playable tiles (192 cells) to 20 × 16 (320 tiles), covering the Game Gear's entire visible 160 × 144 screen except the title and bottom instruction line.

- Z80 current field: 22 × 18 = 396 bytes at `C200`; separate 396-byte next-state buffer at `C400`.
- Three 1-bit sources: Red (2,2), Green (19,2), Blue (10,15), with 1-based field coordinates. Z80 seeds them in machine RAM.
- Each update is executed by the Z80 with real 8-bit opcodes: `NEXT(x,y) = CURRENT | WEST | EAST | NORTH | SOUTH`, then buffers are copied and Game Gear VRAM tiles written.
- `C110` = 11-hop receipt; `C111` = completed wave cycles; `C112` = maximum observed hop. The hop distance witness saturates at 34 even if the player continues running.
- In the attract demonstration (before Z has been pressed), the field resets/reseeds after 34 hop updates. Pressing Z commits a player event and disables the automatic reset until Start begins another round.
- Player cursor Z80 game controls: arrows movement, Z paints selected channel, X cycles red/green/blue, Enter/Start resets the colored field and retains score.
- Reactor at (10,8) awards one point for fully white RGB only after the user paints.

## What we actually measured

These measurements come from executing the compiled **original Z80 cartridge** and independently checking each cell against the expected four-neighbor reach:

| Stage | Colored cells | Fully white cells | Red max reach | Green max reach | Blue max reach |
|---|---:|---:|---:|---:|---:|
| 0 | 3 | 0 | 0 | 0 | 0 |
| 11 | 319 | 1 | 11 | 11 | 11 |
| 24 | 320 | 248 | 24 | 24 | 24 |
| 32 | 320 | 320 | 32 | 32 | 24 |

**Key distinction:** At 11 hops almost every tile was *reached*, but almost none were *fully RGB mixed*. Red and green's farthest cells are 32 Manhattan hops from their respective origins; blue's farthest is 24. The entire screen reaches the white mask by hop 32. At 34, the unpainted experiment begins another wave.

**Independent Z80/reference result:** 34 stages (0–33) × 320 cells = **10,880 checked cell states; zero mismatches**. The separate [33-case regression suite](./tests/rgb-diffusion-11.test.js) also checked runtime memory boundaries, 11-hop witness, reaches, 34-hop recycling, hardware input, painting at (20,16), scored reactor, and Start. The compiled `.gg` was fetched back from GitHub, matched the current assembler output byte-for-byte, and executed again on our emulator.

## Visual design

The only **new cubit indicator** on the hollow-glass page is an 11-hop measurement rail. It advances with the real Z80 `C10E` hop counter and marks the 11-hop witness at approximately one-third of the 34-hop horizon. The sidebar separately reads actual Z80 field RAM to show RGB maximum reach and colored/white coverage; the sidebar doesn't perform game physics.

The page still offers **PLAY RGB DIFFUSION ARENA** for the original 16 × 12 game, **I-13 HELLO WORLD**, **I-13 TECH-001**, **First Light**, and the built-in hardware diagnostic. Original release is preserved at [`freeze/gg-zero-rgb-diffusion-v0.3`](https://github.com/DavidWise01/oasis/tree/freeze/gg-zero-rgb-diffusion-v0.3).

## Rebuild

From `apps/game-gear-zero`:

```bash
node scripts/compile-rgb-diffusion-11.cjs
node tests/rgb-diffusion-11.test.js
```

No ROM/BIOS/third-party emulator is shipped. This is an **original machine-code cartridge** generated using a hand-written Z80 assembler in JavaScript. The source `.i13` describes the numeric mapping, not a full I13-H1.1 f64 compiler, and the results do not establish physical diffusion or actual quantum hardware.
