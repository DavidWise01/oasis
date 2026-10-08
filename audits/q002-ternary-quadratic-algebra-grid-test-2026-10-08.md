# ?002 permutation stations — finite algebra test (2026-10-08)

## Pinned ROOT0 sources
- DavidWise01/quantum-box @ 28ce42f4a84365cdf87ca4979469ac3ce98be36b, whisper-lattice.md, blob 10d21a5a5aec65d8b133864467bb35daaf1ef80c. Three active states (-1,0,+1), Light/Shadow/Inner observers, standing wave 27 00 -27 00, unity goal. This source specifies semantic phase labels and qualitative operations, not a quadratic multiplication table.
- DavidWise01/tetraktys @ e3018c5b67f169af4c82865726353a91426f1ac8, sim/universe.py blob aeb831a40cbefbf003aaea62f9de00f074641a6c. 8x8x8 512-node 6-neighbor toroidal oscillator; sin phase dynamics, damping, forced flip, global coherence-lock feedback. Not a nine-state quadratic algebra.

## ?002 KAEL candidate algebra
A_{a,b} = Z[x] / (x² − ax − b).
(u,v)*(p,q) = (up+bvq, uq+pv+avq).
N(u,v)=u²+auv−bv².
P2(a,b)=(a²+2b,−b²), parameter-grid a,b in {-1,0,1}.

## Independently executed exact integer enumeration in sandbox
Norm multiplicativity N(z*w)=N(z)N(w) for a,b,u,v,p,q each in {-1,0,1}: 729 / 729 PASS.
P2 grid outcomes:
(-1,-1)->(-1,-1) in; (-1,0)->(1,0) in; (-1,1)->(3,-1) out
(0,-1)->(-2,-1) out; (0,0)->(0,0) in; (0,1)->(2,-1) out
(1,-1)->(-1,-1) in; (1,0)->(1,0) in; (1,1)->(3,-1) out.
Grid closure 5/9; failures 4/9. This DOES NOT invalidate KAEL's quadratic algebra or the P2 map defined on wider coefficient integers. It rules out treating P2 as a self-permutation of the exact finite K3² parameter grid.

## Comparison verdict
Whisper's ternary semantic states ≠ KAEL's nine pairs of ring parameters; Tetraktys phase flow ≠ KAEL's product structure. No legitimate operation-preserving bijection specified yet. Shared number 3 or visually reminiscent torus is level-D analogy.
To test a true correspondence, retrieve an earlier ROOT0 source with explicit ring/group operation table and find an explicit homomorphism and preserved invariants.
For ?001 OpenAI continuous incompressible box routing, a simple finite-state permutation is also not sufficient; explicit embedding plus PDE invariants required.

## Stations
ROOT0 Git source: evidenced; purported crawler ingestion: no evidence; agentic transform: no evidence; Reddit publication: evidenced; formal comparison: partial and falsifiable. Do not infer causality.
