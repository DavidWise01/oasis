# GG-ZERO — Hollow Glass / Original Game Gear Emulator

**No EmulatorJS. No Genesis Plus GX. No third-party emulation engine.**

This is an original, experimental Sega Game Gear machine emulator written in JavaScript. It is intentionally independent of the AEON NES project, and the **glass enclosure is UI around real emulation logic**, not the emulation itself.

## Try it

**[Open GG-ZERO on GitHub Pages](https://davidwise01.github.io/oasis/apps/game-gear-zero/)**

Click **RUN BUILT-IN TEST ROM** first. The generated 16 KiB cartridge contains real Z80 machine instructions, not a mocked image. The Z80 writes Mode-4 video registers, a 12-bit Game Gear palette, tile patterns and a name table through Game Gear I/O ports. The emulated VDP then creates a red/blue LCD pattern at 160 × 144. When work RAM becomes `0xA5`, the built-in diagnostic announces success.

You can also load a legitimately obtained `.gg` ROM. It is processed locally and never uploaded. **Most commercial ROMs are not expected to work correctly yet**, because the CPU, timing, mapper and VDP are still partial.

Controls: arrow keys (direction), Z (button 1), X (button 2), Enter (Start). On-screen glass buttons also work. Audio unlocks after clicking **ENABLE SOUND**.

## Real internals

| Module | Implemented | Missing / limitations |
|---|---|---|
| `core/z80.js` | Original Z80 unprefixed opcode interpreter, CB operations, selected ED operations, flags, stack, jumps, I/O, IM1-style IRQ | DD/FD index instructions, much of ED/block I/O, exhaustive flag/timing accuracy |
| `core/gg.js` | ROM bank mapping, 8 KiB mirrored RAM, active-low Game Gear controls, VDP ports, VRAM, 12-bit CRAM, Mode-4 tiled background, basic sprite renderer, CPU frame stepping | alternative cartridge mappers, exact interrupt/raster timing, complete sprite masking/collision logic |
| `core/gg.js` PSG | 3 square channels, simplified noise, attenuation, stereo steering and generated PCM | cycle-accurate SN76489 noise/timing, oscillator envelope/filters |
| `core/selftest.js` | Genuine generated Z80 program that exercises VDP and writes RAM signature | only tests a narrow subset; does not demonstrate real commercial game compatibility |
| `index.html` | Hollow-glass controls, ROM loader, screen, audio unlock, diagnostic, CPU/frame/status monitoring | no save states or debugger yet |

The Game Gear viewport is 160 × 144 pixels, cut from the 256 × 192 Mode-4 background. The 12-bit CRAM converts RGB channels in 0–15 steps to 0–255 display values. Frame timing is approximate (262 lines × 228 Z80 T-states).

## Repeatable tests

From this folder:

```sh
node tests/core.test.js
```

The 17-test suite checks opcode execution, jump targets, I/O bus writes, mapper/RAM behavior, controls, VDP ports, CRAM color, PSG buffer and the booted diagnostic ROM.

A separate **page-level integration test** simulated the browser controls and verified that pressing the diagnostic button executed eight real emulation frames, set work RAM to `0xA5`, and produced the two VDP-derived colors without JavaScript errors.

This is an **initial core milestone**, not an emulator capable of the full commercial catalog. Work forward by adding DD/FD prefix handling, ED instruction groups, accurate VDP IRQs, then commercial ROM verification.

## Publication

Stored under `apps/game-gear-zero/` in `DavidWise01/oasis`, without changing OASIS's root page or AEON's separate NES project. No copyrighted game ROM or BIOS is committed.
