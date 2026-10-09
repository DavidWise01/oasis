# P3.52 — Envelope reconciliation

Confirmed sequences (user supplied): total `60/24/12/2/1/1/0/0`; boxy `10/6/8/4/2/1/1/0/0`; circle `11/9/7/5/4/3/2/1/1/0/0`. Mixed-radix active capacity respectively 34,560; 3,840; 83,160; 121,560 combined across distinct enclosures, two pinned zero sentinels each. Preserve independent 48 carrier channels (four colored primes × six axes × two signs) and 1,440-step Möbius traversal. No automatic physical inference.

Local Node test PASS, 121,560 envelope-index round trips and 207,360 representative carrier/axis/rotation round trips. 328,920 total checks as counted in test. The 207,360 tests sample addresses rather than exhaustively visiting every envelope address × every channel × every time step.

Both GitHub source and test files were explicitly updated from initially empty commits to substantive code. Remote CI not claimed.
