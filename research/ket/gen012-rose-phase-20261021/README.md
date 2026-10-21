# KET Gen0–Gen2 :: rose-centered 8×3 phase motion

Pinned origin: `0vwxyz`. Three generations, two signed choices each: `--- --+ -+- -++ +-- +-+ ++- +++`. Three color bands: H/orange, O/indigo, N/teal; 8×3 = 24 fixed identity positions. This is a symbolic model, not demonstrated quantum physics.

Geometry: moving 5D toroid contains one 3D box, which may contain the *projection* of a 4D tesseract. Shadow predicate is unspecified and no shadow is automatically materialized. `−/+2.5` weak coupling windows: 122–125, 140–145, 360–366 (symbolic only). Internal radix is selectable 1..60; unary is non-positional.

## Next operation: toroidal phase motion

State key = (path, band, phase_bin). Phase = 0..59. `advance(t) = (phase_bin + t) mod 60`; identity and rose origin remain fixed. Every 60 increments closes a phase cycle, reverse steps restore the original state, and no shadow is inferred from rotation. There are 24×60 = 1,440 discrete phase-address combinations; this does **not** assert that physical motion produces 1,440 distinguishable quantum states.

Run `python phase_v2.py` to regenerate the deterministic result. The 5 assertions test identity uniqueness, cycle closure, reversibility, forward/backward wrap, and preservation of origin/shadow policy.

This directory appends a new checkpoint without modifying prior frozen baselines. Physical wavelength bindings and three-photon entanglement remain hypotheses, not measured validations.
