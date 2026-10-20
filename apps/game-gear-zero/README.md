# GG-ZERO — Hollow Glass / Original Game Gear Emulator

**No EmulatorJS. No Genesis Plus GX. No third-party emulation engine.**

This is an original, experimental Sega Game Gear machine emulator written in JavaScript. It is intentionally independent of the AEON NES project, and the **glass enclosure is UI around real emulation logic**, not the emulation itself.

## Try it

**[Open GG-ZERO on GitHub Pages](https://davidwise01.github.io/oasis/apps/game-gear-zero/)**

Click **RUN BUILT-IN TEST ROM** first. The generated 16 KiB cartridge contains real Z80 machine instructions, not a mocked image. The Z80 writes Mode-4 video registers, a 12-bit Game Gear palette, tile patterns and a name table through Game Gear I/O ports. The emulated VDP then creates a red/blue LCD pattern at 160 × 144. When work RAM becomes `0xA5`, the built-in diagnostic announces success.

You can also load a legitimately obtained `.gg` ROM. It is processed locally and never uploaded. **Most commercial ROMs are not expected to work correctly yet**, because the CPU, timing, mapper and VDP are still partial.

Controls: arrow keys (direction), Z (button 1), X (button 2), Enter (Start). On-screen glass buttons also work. Audio unlocks after clicking **ENABLE SOUND**.

## COMPILED RELEASE — ready-to-load Game Gear ROM

- [**Download the 16 KiB compiled I-13 HELLO WORLD .gg**](./dist/i13-hello-world-rgb.gg)
- [Reproducible build instructions and SHA-256](./dist/README.md)
- [No-dependency Node build script](./scripts/compile-i13-hello-world.cjs)

The committed binary was fetched back from GitHub, checked byte-for-byte against the source generator, and executed on our emulated Z80 through all eight RGB phases, reversal and freeze. Its SHA-256 is `a42fd461d6555f528d70ca54e5277a90f2739bf899352bff8e571baa878f0d6d`. The compiled release is a bounded **hand translation** of the I-13 numeric source, not a general I13-H1.1 compiler.

## RGB DIFFUSION 11 — measured 20×16 field

**[Play RGB Diffusion 11 automatically in the hollow-glass Game Gear](https://davidwise01.github.io/oasis/apps/game-gear-zero/)** · [Compiled 16 KiB `.gg`](./dist/rgb-diffusion-11.gg) · [Source and measurement report](./RGB-DIFFUSION-11.md) · [I-13 numeric notation](./examples/i13-rgb-diffusion-11.i13)

The new default Z80 cartridge expands RGB from 192 to **320 cells**, follows three separate one-bit channels (8 mask states), and records an explicit **11-hop witness**. The four-cardinal-neighbor core is the provisional implementation of `11 {2/2|{4|/2/2}`, not a claimed canonical definition. The three sources continue to propagate to their farthest corners: red/green each reach **32** Manhattan hops, blue reaches **24**.

At hop 11, **319 cells are colored but only 1 is fully white**. By hop 32, all **320 cells are white**. The actual original Z80 ROM matched an independent 34-stage/320-cell mathematical reference in **10,880/10,880 comparisons** with **0 mismatches**. A separate **33/33 regression test** checks controls, extended display, scoring, hop witness, resets and old-game compatibility. The Z80 cycles fresh wavefronts after 34 hops until the user paints.

**New glass cubit indicator:** a real CPU-driven 11-hop measurement rail. The earlier game is still available as **PLAY RGB DIFFUSION ARENA**, and the v0.3 baseline is preserved at `freeze/gg-zero-rgb-diffusion-v0.3`.

Recompile with `node scripts/compile-rgb-diffusion-11.cjs`, validate with `node tests/rgb-diffusion-11.test.js`. The `.i13` file is a source intent specification, while the executable is a bounded Z80 hand translation rather than a full I13 f64 VM. This is classical cellular propagation, **not a physical quantum diffusion experiment**.

## RGB DIFFUSION ARENA — original playable Z80 game

**[Play immediately in the hollow-glass Game Gear](https://davidwise01.github.io/oasis/apps/game-gear-zero/)** · [Compiled 16 KiB `.gg` cartridge](./dist/rgb-diffusion-arena.gg) · [Game instructions and implementation](./RGB-DIFFUSION.md)

GG-ZERO now boots **RGB Diffusion Arena by default**. Three seeded colors expand through a 16×12 Game Gear tile field. The Z80 computes a synchronous four-neighbor RGB-bitmask propagation step every six frames, sends the resulting tiles through the emulated VDP and waits for the player to paint. **Arrows** move, **Z** paints the current RGB bit, **X** cycles R/G/B, and **Start** restarts the seeded round. Reaching white at the reactor earns a point only after a player paint event. In attract mode the waves repeat automatically, so the game stays visually alive.

This is a **classical binary RGB propagation game**—not a physical diffusion solver or quantum device. The I-13 `.i13` file expresses numeric intent; the actual ROM is a bounded hand-assembled Z80 translation, not an implementation of the complete I13-H1.1 VM.

**Verified:** 27/27 original Z80/VDP/gameplay regression tests, page integration (movement, ink changes, Z80-scored white reactor, glass winner halo, Start and all existing cartridges), and the compiled binary fetched from GitHub matching its source generator byte-for-byte.

Compile locally with `node scripts/compile-rgb-diffusion.cjs`; the ROM is already committed in `dist/`.

## HELLO WORLD · I-13 RGB diffusion dot

[**Open the GG-ZERO page and choose I-13 HELLO WORLD · . RGB**](https://davidwise01.github.io/oasis/apps/game-gear-zero/) · [Full specification](./I13-HELLO-WORLD.md)

The Game Gear runs an original 16 KiB Z80 cartridge that **renders HELLO WORLD using hardware Mode-4 font tiles**, shows the eight RGB signed-pair combinations from \`. = 2^3\`, and changes a central dot's RGB444 palette through emulated Z80 I/O. **← IN (−)** reverses the color cycle; **→ OUT (+)** advances; **Z** freezes the dot. All three hollow-glass RGB indicators read the actual machine RAM bits.

The [\`.i13\` numerical source](./examples/i13-hello-world.i13) follows I13-H1.1 source conventions, but is **hand-translated into a bounded Z80 cartridge**; this is not a port of the full f64 I13 VM or a physical quantum-dot model.

**Tests:** \`node tests/i13-hello-world.test.js\` — 25/25 passed, including all eight states, REAL VDP characters, IN/OUT wrap and freeze. Page-level integration also passed, including switching back to the two existing working cartridges.

## I-13 · executable Z80 kernel (GG adapter)

[**Run I-13 on the hollow-glass Game Gear page**](https://davidwise01.github.io/oasis/apps/game-gear-zero/) or read [I13-Z80.md](./I13-Z80.md).

**RUN I-13 ON Z80** launches a newly assembled 16 KiB \`.gg\` cartridge that executes a bounded copy of the authoritative I13-H1.1 **E1.TECH-001** trit authority law on our actual emulated Z80: \`−1 HOLD\`, \`0 FLAY\`, \`+1 PROCEED\`. Left/Up/Right choose the evidence trit; button 1 adds question debt, button 2 clears it. Signed trit validation, RAM witnesses, VBlank IRQ and red/amber/green LCD palette writes are performed by Z80 instructions, not by the HTML panel.

**Scope:** executable signed-trit subset of I-13, **not** full I13 f64 VM, 15-opcode bytecode interpreter, Rust/Wasm Cortex or E1 external services. Canonical source in [I13-H1.1](https://github.com/DavidWise01/I13-H1.1) is unchanged. \`p1\` does not bypass a separate host capability gate.

**Checks:** 25 isolated on-emulator truth/guard/VDP/IRQ tests plus an integrated page-level controller test passed. First Light still boots, and its pre-port baseline is frozen as \`freeze/gg-zero-first-light-v0.2\`.


## FIRST LIGHT — first original playable cartridge

[**Play First Light on GG-ZERO Pages**](https://davidwise01.github.io/oasis/apps/game-gear-zero/)

The **PLAY FIRST LIGHT** button assembles and boots a 16 KiB Sega Game Gear \`.gg\` ROM made entirely of Z80 instructions and ROM graphics. **DOWNLOAD FIRST LIGHT .GG** exports the same binary for inspection or use in another compatible emulator. No commercial game code, images, sounds or ROMs are included.

**Game:** steer a luminous crystal through a 20 × 18 tile maze. The viewport is rendered by the Game Gear VDP from tiles and sprite registers. The maze lives as a 32 × 24 collision table inside the cartridge ROM. CPU instructions compute the prospective grid location, look up the collision byte and reject wall cells. Input is read from emulated port \`0xDC\`.

**Keyboard:** arrows move one tile per seven serviced frames; **Z / button 1** shifts the palette toward cyan and plays a square-wave tone; **X / button 2** shifts the palette to magenta with a different tone. Releasing both returns the PSG volume to silence. Game Gear Start remains connected to the hardware input port, but this cartridge has no Start-specific game action.

**Game engineering:** \`games/first-light.js\` assembles original machine code, prepares tile graphics and palette data, positions a hardware sprite, and runs a \`EI → HALT → VBlank IRQ → RETI → TICK\` loop. The IRQ routine at ROM vector \`0038h\` increments a RAM witness counter. The shell's **one new graphical change** is a brief glass pulse on each twelfth serviced VBlank interrupt (not an arbitrary CSS timer).

**Hardware inspector:** reads live Z80 \`AF, BC, DE, HL, SP, PC\`, tracks VDP VRAM/CRAM writes, PSG and input-port transactions, IRQ requests and serviced interrupts, plus current player tile, collision count and ability mode.

**Regression evidence:** \`node tests/first-light.test.js\` provides 18 passing CPU/ROM/VDP/PSG/collision/IRQ cases. The existing 17-case base suite remains separate. A page-level instrumented browser simulation also passed actual button delivery, wall blocking, both abilities, scheduled nonzero PSG audio buffers, CPU register telemetry and the VBlank-driven glass marker. **Real device speaker output and a physical Game Gear are not yet verified.** Full commercial ROM compatibility remains outside this milestone.

Previous base release is preserved as Git branch [\`freeze/gg-zero-v0.1-core\`](https://github.com/DavidWise01/oasis/tree/freeze/gg-zero-v0.1-core).

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

For First Light, additionally run `node tests/first-light.test.js`. That suite has 18 checks for an original cartridge, Z80 interrupts, maze collisions and PSG tones.



From this folder:

```sh
node tests/core.test.js
```

The 17-test suite checks opcode execution, jump targets, I/O bus writes, mapper/RAM behavior, controls, VDP ports, CRAM color, PSG buffer and the booted diagnostic ROM.

A separate **page-level integration test** simulated the browser controls and verified that pressing the diagnostic button executed eight real emulation frames, set work RAM to `0xA5`, and produced the two VDP-derived colors without JavaScript errors.

This is an **initial core milestone**, not an emulator capable of the full commercial catalog. Work forward by adding DD/FD prefix handling, ED instruction groups, accurate VDP IRQs, then commercial ROM verification.

## Publication

Stored under `apps/game-gear-zero/` in `DavidWise01/oasis`, without changing OASIS's root page or AEON's separate NES project. No copyrighted game ROM or BIOS is committed.
