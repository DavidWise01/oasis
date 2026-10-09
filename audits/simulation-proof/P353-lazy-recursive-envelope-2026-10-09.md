# P3.53 — Lazy recursive envelope

Preserve the exact envelope sequences total 60:24:12:2:1:1:0:0, boxy 10:6:8:4:2:1:1:0:0, circle 11:9:7:5:4:3:2:1:1:0:0. Retain exact symbolic primitive {{1/8 x 1/8}}^{{n}} = 64^-n. Pinned zeros are address sentinels; root 0 fixed. Four primes, six axes, two signs: 48 carrier labels, independently addressable. Mobius traversal 4x360=1440, separately retained.

Executed Node test: PASS 121560 mixed-radix structural round trips; 11520 deeper sampled/streamed tests, including n=1024, without materializing a full recursive lattice. The implementation restricts n<=10000 for computational practicality. Numerical correctness here is about symbolic indexing, not physics. Remote CI is not verified.
