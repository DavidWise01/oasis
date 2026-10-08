# SHEET 76 — Plank Bouncer / nesting wave adapter

Append-only successor to SHEET75; uses user-provided compiled React visualization as source provenance. User title **Plank Bouncer** preserved (not silently renamed to Planck). The artifact states **416 bodies per level** divided into strong 300 / medium 100 / weak 16, with nested gravity-well shells and inner shells breathing **4× faster**. Its explicit visual shell expression is `radius = 0.6 + 0.4*sin(phase)`.

### Adapter

Four finite demonstration levels use `r_l(t) = 0.6 + 0.4 sin(2π * 4^l * t/256)`; this yields 1, 4, 16, 64 full oscillations per 256-tick master cycle. Every shell remains within radius 0.2–1.0. The previous 60-position C60 register is retained via 15 quads / three groups / one root / one digest; rotate +15 and XOR1 four times to close its exact digital state. The 9/6/1 and sqrt(1.25) scheduling metadata are unchanged.

Local tested Python passed **24/24** checks, covering bounded shell oscillation, reversibility, registry and binary state identity, tamper rejection and deterministic commitments. The executable is committed as `benchmark.py` and can be replayed with `python benchmark.py`.

### Scope limit

This **does not** simulate actual Planck-length physics, derive a gravitational field equation, demonstrate infinite real-world nested objects, or prove a closed gravity orbit. Shells and register are independently periodic in this adapter. Registry is represented as 416 symbolic identities per chosen level, *not* fully expanded 416^depth storage.
