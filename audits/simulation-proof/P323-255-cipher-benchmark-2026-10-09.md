# P3.23 — 255-stage demonstration cipher + pinned root
Date: 2026-10-09

Corrected count: 255 non-root reversible operations (1–255) plus root index 0, total 256. Operations alternate across `-+- /\\ +-+` with 128 operations on the left port and 127 on the right. Each is a norm-preserving complex two-port rotation with a separately generated phase; inverse order traverses 255 down to 1.

**Local executed test:** 12,000 seeded randomized three-port complex states; maximum norm discrepancy 3.064215547965432e-14, maximum inverse component error 8.992806499463768e-15; 0 failing cases. Starting unit traveling amplitude yields channel intensities approx 0.9114244791, 0.0866302843, 0.00194523659. Validation concerns only the generated operation policy; the user's original authoritative 255 token/operator meanings remain unspecified, so this is not proof that those original 255 operations were implemented. The 208-step count remains superseded. No physical Stargate, Planck transport, or Dyson extraction is established. The P3.7 voltage wrapper remains unchanged.

Next: define operator semantics per stage and integrate the authenticated address/ledger pipeline, preserving separate capture ports.
