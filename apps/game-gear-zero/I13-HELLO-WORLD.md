# I-13 Hello World · RGB diffusion dot · GG-ZERO

**Status:** original self-assembled 16 KiB Game Gear cartridge implemented, 25/25 ROM/CPU/VDP/direction/freeze checks passing, page-level integration test passing.

This is a **classical software** visualization of the proposed symbolic dot. **No physical quantum, photon, semiconductor, or diffusion claim** is established by it.

## Dot and three paired channels

Literal model:

    . = 2^3 = 8 states

          RED       GREEN       BLUE
        { - + }    { - + }     { - + }
          bit0       bit1        bit2

        IN - : state = (state - 1) & 7
        OUT+: state = (state + 1) & 7

\`−\` = unlit bit (0). \`+\` = lit bit (1). State address is \`R + 2*G + 4*B\`, starting at 0 and wrapping after 7.

| State | Red | Green | Blue | RGB (8-bit/channel) |
|---:|:---:|:---:|:---:|---|
| 0 | − | − | − | 0,0,0 |
| 1 | + | − | − | 255,0,0 |
| 2 | − | + | − | 0,255,0 |
| 3 | + | + | − | 255,255,0 |
| 4 | − | − | + | 0,0,255 |
| 5 | + | − | + | 255,0,255 |
| 6 | − | + | + | 0,255,255 |
| 7 | + | + | + | 255,255,255 |

Note: the *eight swatches* are 8 tile patterns with palette indexes 1..8. A *ninth active dot* uses palette index 9; the Z80 repaints that palette entry each state change. The letter tiles use a fixed white-blue palette entry 10 and the dot edge uses palette index 15.

## Source and executable build

- [Numerical I13 source intent](./examples/i13-hello-world.i13) uses the canonical \`I name <- numeric expression\` form from [I13-H1.1](https://github.com/DavidWise01/I13-H1.1) and preserves I-13's thirteen semantic words. It contains numeric symbols and ASCII witnesses for the HELLO WORLD text.
- [Z80 cartridge assembler](./games/i13-hello-world.js) is the **explicit hand translation** of the bounded color-state semantics into machine code. It generates the glyph tile bitmaps, all eight swatch patterns, palette lookup table and 16 KiB \`.gg\` ROM.
- The cartridge itself executes on **our** [Z80](./core/z80.js), not EmulatorJS or an external Game Gear implementation. CPU writes travel via \`OUT 0xBF\` / \`OUT 0xBE\` to the [original VDP](./core/gg.js).

This is **not** a compiler-generated full I13-H1.1 executable, its 15-opcode f64 VM, or the Cortex/CV runtime. The first I13-powered Z80 reference was the earlier TECH-001 signed-trit cartridge; this release adds an eight-state RGB program.

## What the program executes

1. Reset vector \`0000h\` jumps to \`0100h\` and VBlank ISR at \`0038h\` counts serviced interrupts.
2. The CPU copies a 12-bit color RAM palette, 8×8 dot and letter tiles, and the 32×24 Mode-4 name table through VDP ports. Actual GAME GEAR viewport is the 160×144 center crop.
3. The Z80 writes \`0xA5\` at work RAM \`C125\` after graphic initialization.
4. Each VBlank the CPU reads real emulated \`0xDC\` gamepad input. Every twelfth frame it steps the active dot; \`LEFT\` selects IN decrement, \`RIGHT\` selects OUT increment, and button 1/Z freezes the phase while held.
5. Each step computes \`(phase + direction) & 7\`, uses the phase as a ROM color-table index, and writes its 2-byte RGB444 color to CRAM index 9.
6. The page inspector **reads**, but never assigns, the Z80 RAM phase, direction, step count and freeze bit. The three glass lamps are the sole new visual shell element and are driven by the actual RAM RGB bits.

## State registers

| RAM | Contents |
|---|---|
| C120 | 3-bit RGB phase, 0..7 |
| C121 | signed direction, \`0xFF\` for IN(-1), \`0x01\` for OUT(+1) |
| C122 | 12-frame divider |
| C123 | step counter (8-bit rollover) |
| C124 | active-low raw gamepad input |
| C125 | boot marker \`0xA5\` |
| C126 | serviced VBlank count (8-bit rollover) |
| C127 | input freeze bit, 0 or 1 |

## Controls

- **←** sets IN − (decrement / reverse cycle)
- **→** sets OUT + (increment / forward cycle)
- **Z / Button 1** holds current phase and stops RGB diffusion while pressed
- **RUN I-13 HELLO WORLD** assembles/boots the ROM
- **DOWNLOAD HELLO .GG** exports the generated machine code to disk
- **RUN I-13 ON Z80** returns to the previous TECH-001 signed-trit cartridge
- **PLAY FIRST LIGHT** returns to the game without modifying its source

## Validation

The committed [25-case regression suite](./tests/i13-hello-world.test.js) executed the original Z80 cartridge and checked boot, tilemap HELLO WORLD glyphs, 8 dot swatches, all eight phases \`1,2,3,4,5,6,7,0\`, both direction changes, hold/release, source bits, computed palettes and real VBlank handler.

A separate **page-level simulated-browser integration** clicked the new launch button and verified, via actual emulator execution, phase 0 boot, phase 1 red lamp, IN reverse to 0, Z freeze, OUT resume to 1, and successful switching to the prior I13 TECH-001 and First Light cartridges.

Scope: core-backed, tested Z80/VDP execution. It is not a physical Game Gear or real speaker/quantum-dot test. GitHub Pages deployment may lag the commits.

## Compatibility and freeze

The prior First Light working release is preserved on [\`freeze/gg-zero-first-light-v0.2\`](https://github.com/DavidWise01/oasis/tree/freeze/gg-zero-first-light-v0.2). The previous \`I13 TECH-001\` cartridge files are unchanged. Nothing here mutates the authoritative I13-H1.1 repository.
