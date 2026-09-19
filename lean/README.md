# OaSIs Lean kernel

Deterministic Root0/Oasis language formalization.

Current chain:

- `Oasis.Language.Cube.00.lean` — language cube kernel and `|`, `||`, `|||` delimiter surface
- `Oasis.Language.OSI1.00.lean` — carrier
- `Oasis.Language.OSI2.00.lean` — 20-bit framing
- `Oasis.Language.OSI3.00.lean` — address/routing rail
- `Oasis.Language.OSI4.00.lean` — deterministic ordering
- `Oasis.Language.OSI5.00.lean` — session/bind
- `Oasis.Language.OSI6.00.lean` — 104-bit language representation + 20-bit frame = 124-bit OSI body
- `Oasis.Language.OSI7.00.lean` — `|||` boundary to HACI / Layer 8

Validated locally by Lean where marked in development conversation; OSI6 is the current next validation target.
