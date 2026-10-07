# OASIS Symbiot OS / AVA Alignment — v33

## Decision

KEEP as a real executable-source ancestor, with strict separation among:
1. the Rust no_std x86_64 kernel source,
2. the two 512-byte BIOS boot-sector stubs,
3. the browser stack toy simulator.

## Source receipt

Connected GitHub source:
- repo: DavidWise01/symbiot-os
- head: e1d3567ab1fbf16b75f7aafc10832850248163f6
- src/main.rs is a real no_std/no_main Rust kernel using bootloader, VGA 0xb8000, IDT, 8259 PIC remap, PS/2 IRQ1, and a six-phase state machine.

Phase cycle:
SEED -> PUSH -> TRACE -> PRUNE -> RETURN -> GROUND -> SEED

## State-machine findings

- six autonomous phase steps return to the original phase: PASS
- source computes wobble = 2 + (witness & 0x03), so pre-clamp wobble is 2..5
- README prose says 2..4
- apply_cmd('G') changes phase only; it does not clamp wobble/coherence
- Ground clamp occurs only inside tick() when the post-next phase is Ground

Probe:
wobble=5/coherence=96 + command G -> Ground/5/96, not Ground/2/98.

## Witness finding

The source uses 32-bit FNV-1a over four bytes of a mixed 32-bit state seed.
It is retained as a deterministic witness tag, not cryptographic proof.

Exact source-formula reproduction found a repeated witness:
- cycle 13900
- cycle 60109
- value 895685730 (0x3563e362)

So witness equality is not state identity.

## CI/build receipt

Latest connected GitHub build for symbiot-os head e1d3567...:
- workflow run 30284092253
- conclusion: FAILURE
- failed step: cargo build
- x86_64 0.14.13 fails against current moving nightly because Step now requires forward_overflowing/backward_overflowing.

The historical 2026-05-15 build statement is therefore not a current green-CI certificate. The toolchain file itself already recommends pinning nightly-2026-05-15 if future nightly breaks.

## Uploaded boot sectors

symbiosis_boot.bin:
- 512 bytes
- SHA-256 c47942e51408410ad8078efe81cc646fff850fdbf2966ee47b78e17b592511c0
- Git blob aabcd9172358bd7d6cf99a56184b36dcc5640b71
- 55aa signature

symbiosis_boot_FIXED.bin:
- 512 bytes
- SHA-256 c419d3bdab44662157347445f7b9b538fc288b2a3905c3bfd0082e4f818772f8
- Git blob f4c9f2c71c4cb8a475f1619b3b2f275524bd7705
- 55aa signature

Both uploads exactly match the blobs in symbiot-os.

Static 16-bit audit:
- LODSB at offset 3
- short print-loop jump target = offset 2 in both
- original text starts offset 20 but SI starts offset 30
- FIXED text starts offset 22 but SI starts offset 23

They are legacy BIOS stubs, not the Cargo bootimage of the Rust kernel.

## Browser simulator

The HTML explicitly labels its numbers toy-model outputs.

Clock formula:
max(25, 100000/freq) milliseconds

Thus:
- nominal 100 Hz -> 1 Hz timer
- nominal 1 kHz -> 10 Hz timer
- nominal 10 kHz -> 40 Hz timer
- nominal 50 kHz -> 40 Hz timer

So the UI frequency label is not the actual pulse scheduling rate.

## AVA

AVA.md explicitly says AVA is not a compiler target yet. Its useful taxonomy is:
seed -> push -> trace -> prune -> return -> ground -> witness.

v33 narrows "witness proves the cycle happened" to deterministic witness tag.

## OASIS boundary

All Symbiot material remains HOLD-only support. It does not override Root, durable/finality law, verified-only truth advancement, or human authority.

Canonical local monolithic v33 source SHA-256:
921ad86b842a795a863b63f67a58420c54926f46ab719d4b2130181286aa087b

Lean compiler was unavailable in the alignment runtime.
