# SHEET 72 — Binary gravity inversion `/inf/fni/inf\`

Append-only successor to SHEET71. User-specified primitive **1→0, 0→1**, modeled as the involution `flip(b)=b XOR 1`. The toy gravity equation `r''=-mu/r²+lambda*r` remains unchanged; a new **imposed reflective wall** at `rmin=2` guards its radius-zero singularity. Each wall contact toggles the bit. This is a symbolic event/phase latch, not a physical theory of binary gravitation.

Local test: mu=1, lambda=.04, dt=.002, r0=4, v0=-.8, 5000 kick–reflect–kick steps. Exactly one reflected boundary contact occurred at tick 1331; for initial bit 1 this yields 0, and for initial bit 0 it yields 1. The exact `1→0→1` logical sequence uses two bit inversions; **a second physical bounce was not observed**. Reverse integration errors: radius `1.2434497875801753e-14`; velocity `4.3298697960381105e-15`.

The 416 source registry identifiers (300 strong, 100 medium, 16 weak) are unchanged. `9/6/1` hierarchy and `sqrt(1.25)` occupancy threshold are retained as independent kernel control metadata. Executed local benchmark **20/20 checks passed**. Source benchmark and full JSON are available in the accompanying conversation ZIP. These are not evidence for cosmological turnaround, real gravitational bit inversion or physically continuous spacetime transitions. SHA256 integrity is not authentication.

Benchmark SHA256 (local exact source): `a8934f36951f40f560ee1c2ed44ebaa46af759b2be8000f1f6cc48de58af69f2`.
