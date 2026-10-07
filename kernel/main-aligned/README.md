# OASIS Main Aligned Kernel

Current logical alignment: **v33 — Symbiot OS / AVA**.

Canonical monolithic v33 source SHA-256:
`921ad86b842a795a863b63f67a58420c54926f46ab719d4b2130181286aa087b`

Browseable v33 module:
`lean/Oasis.Fallout.Symbiot.v33.lean`

Detailed v33 report/manifest/audit:
`kernel/main-aligned/v33/`

Important transport note: this commit records the exact v33 source digest and delta artifacts, but does not replace the existing binary `CURRENT.lean.gz` transport snapshot. Treat that binary as legacy until a later binary-safe promotion. The v33 standalone module/report/manifest are the Git-visible current alignment records.

v33 findings:
- real no_std x86_64 Rust source exists in DavidWise01/symbiot-os
- six-phase cycle SEED→PUSH→TRACE→PRUNE→RETURN→GROUND
- source wobble is 2..5 before Ground clamp, not README 2..4
- keyboard G changes phase only; it does not itself clamp
- 32-bit FNV witness is a tag, not uniqueness/proof
- current symbiot-os GitHub CI is red against moving nightly
- uploaded 512-byte boot stubs are legacy BIOS fixtures, separate from Cargo bootimage
- browser stack model remains toy-model only

All aligned support remains HOLD-only.
