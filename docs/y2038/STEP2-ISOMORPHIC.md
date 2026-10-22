# Isomorphic Step 2 — {{i..}} projection audit

[Open interactive encoder](step2-isomorphic.html) · [Original Step 2](step2.html) · [Möbius spinor](mobius-spinor.html)

Canonical seconds `t` are represented losslessly using Euclidean division by 86400:

- `q=floor(t/86400)`
- `p=t-86400*q`, thus `0<=p<86400`
- `arc=15*p`; `spinor=(-1)^q`
- inverse `t=86400*q+arc/15`, with `arc%15=0`.

A 32-bit legacy port accepts only `-2^31 <= t <= 2^31-1`. A signed 64-bit view accepts `-2^63 <= t <= 2^63-1`. The symbolic envelope can represent larger integers in JavaScript's BigInt, but that does not establish a working 64-bit ABI conversion for those values.

The sign and Möbius surface are conceptual representation metadata. They do not change Unix time physics or solve platform compatibility by themselves.

Inspect source casts, database schema, protocol serialization, and 32-bit consumers separately.
