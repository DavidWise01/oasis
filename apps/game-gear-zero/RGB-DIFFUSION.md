# RGB Diffusion Arena — original Z80 Game Gear game

**[PLAY THE GAME ON THE HOLLOW-GLASS GG-ZERO PAGE](https://davidwise01.github.io/oasis/apps/game-gear-zero/)**

**[Download compiled 16 KiB cartridge](./dist/rgb-diffusion-arena.gg)** · [Source generator](./games/rgb-diffusion-game.js) · [I-13 source intent](./examples/i13-rgb-diffusion.i13)

This is a **real Z80 Game Gear cartridge** which executes an independently colored 16 × 12 tile field. The emulator runs actual Game Gear machine code. It is not a JavaScript canvas effect, nor an imported EmulatorJS or Genesis Plus GX core.

## Play

On opening the page, RGB Diffusion Arena boots automatically, showing three initial colored pulses. Its 16×12 board uses **8 color states** formed by three independent binary channels:

```text
. = 2^3 = 8 RGB states

red   - +     1-bit: 1
green - +     1-bit: 2
blue  - +     1-bit: 4

0 black  1 red    2 green   3 yellow
4 blue   5 magenta 6 cyan   7 white
```

Controls (emulated input ports, interpreted by Z80 instructions):

- **Arrow keys** or glass D-pad: steer the bright crystal.
- **Z / button 1:** paint the selected RGB channel into the tile beneath your crystal.
- **X / button 2:** choose red, then green, then blue, cycling on distinct press edges.
- **Enter / Start:** reset and reseed the board for another round; score is retained.

**Win condition:** bring all three color bits together at the **reactor tile (x=8,y=6)**. A score is awarded **only after the user has painted at least once**. The white-glass victory halo is driven by the Z80 win witness.

Before a player paints, a Z80-managed demonstration resets/reseeds its RGB waves every 20 propagation ticks, so you can watch the field evolving continuously. After the first paint, the field remains active until you press Start.

## Algorithm — actual Z80

Every six emulated frames, the Game Gear CPU computes a full two-buffer cellular-automaton step:

```text
NEXT(x,y) =
    CURRENT(x,y)
  | CURRENT(x−1,y)
  | CURRENT(x+1,y)
  | CURRENT(x,y−1)
  | CURRENT(x,y+1)
```

Cells store only **three bits** of state (red = 1, green = 2, blue = 4). The board uses a padded 18 × 14 RAM region and a separate 18 × 14 next-state buffer to keep each update synchronous. This is a **binary four-neighbor propagation automaton**, inspired by diffusion/mixing. It **does not conserve pigment mass or solve a physical diffusion equation**. Mixing happens through bitwise OR; tiles can accumulate colors until all turn white. Reset starts a new wave.

The Z80 then writes the exact 16×12 tile data to the Game Gear Mode-4 VDP using its `OUT 0xBF`/ `OUT 0xBE` ports; tiles show all eight RGB palette combinations. A hardware sprite marks the cursor; sprite coordinates are also computed by Z80.

**Game RAM:** `C100/C101` = crystal x/y, `C102` = selected RGB bit, `C106` = score, `C107` = `A5` boot witness, `C109` = reactor winner, `C10E` = diffusion ticks, `C10F` = actual player-paint witness, `C200` = 252-byte current field, `C300` = 252-byte next field.

## Compile and test

From `apps/game-gear-zero`:

```shell
node scripts/compile-rgb-diffusion.cjs
node tests/rgb-diffusion.test.js
```

No npm install or external emulator required. The committed `dist/rgb-diffusion-arena.gg` is generated from the exact source.

Verified **27/27 original core tests** include visible RGB spread, keyboard/joypad input, mode-switch debouncing, RGB bitwise mixing and reactor scoring, seeded resetting, periodic attract-mode renewal and real Game Gear VDP writes. Additional page-level simulated browser validation verified **autoplay, changing LCD pixels, a player-earned white reactor, halo signal, reset, and switching to all three prior cartridges**.

## Canonical I-13 boundary

The attached `.i13` example is a numeric *semantic specification* using I13-H1.1 conventions; the playable ROM is a **hand translation into Z80 machine instructions**, not the full 15-opcode I13 f64 VM. All binary RGB diffusion is classical software. No physics or quantum computing result is claimed.

First Light and the earlier TECH-001 and HELLO WORLD cartridges remain unchanged. The baseline branch `freeze/gg-zero-first-light-v0.2` remains intact.
