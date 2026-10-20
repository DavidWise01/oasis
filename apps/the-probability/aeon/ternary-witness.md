# AEON — Ternary Witness

This browser profile enables the eight-port audit in the exact order
`UP, DOWN, LEFT, RIGHT, B, A, SELECT, START`.

```aeon-config
name = "Ternary Witness"
description = "Audit all eight delivered inputs before resolving {-1,0,+1}"
strategy = fight
state_key_mode = screen
tri_state_enabled = true
probe_hold_frames = 2
probe_settle_frames = 3
probe_retry_frames = 180
decision_frames = 4
```

The classifications are observations, not proven game progress.
