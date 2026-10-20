# Compiled I-13 HELLO WORLD Game Gear cartridge

**Artifact:** [i13-hello-world-rgb.gg](./i13-hello-world-rgb.gg)  
**Length:** 16,384 bytes (16 KiB)  
**SHA-256:** `a42fd461d6555f528d70ca54e5277a90f2739bf899352bff8e571baa878f0d6d`  
**Git blob SHA-1:** `f8ce7bccafed76fefc10eadbd0197fdc560f6410`

## Compile from the same committed source

From the `apps/game-gear-zero/` directory:

```shell
node scripts/compile-i13-hello-world.cjs
sha256sum dist/i13-hello-world-rgb.gg
node tests/i13-hello-world.test.js
```

No npm install is required. The script loads [games/i13-hello-world.js](../games/i13-hello-world.js), assembles its deterministic Z80 bytes, checks its reset vector and I-13 RGB metadata, and writes `dist/i13-hello-world-rgb.gg`.

The compiled binary was loaded **directly from the committed GitHub binary** into [our original GG-ZERO emulator](../core/gg.js) and matched the source generator byte for byte. That runtime executed HELLO WORLD, completed phases `1→2→3→4→5→6→7→0`, reversed on LEFT, and froze on button 1.

The `.i13` source in [examples/i13-hello-world.i13](../examples/i13-hello-world.i13) documents the canonical I-13 numeric intent. The executable is a **hand-translated, bounded Z80 cartridge**; this build command is not a general I13-H1.1 compiler. The 8-state `. = 2³` RGB dot is a **classical** visualization, not a physical quantum device.

To run: download the `.gg` file, visit [the GG-ZERO page](https://davidwise01.github.io/oasis/apps/game-gear-zero/) and load it with the file picker (or use the built-in HELLO WORLD button).
