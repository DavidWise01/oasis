# AETHER Phase VI · Turns 121–128

## Objective
Stress the **scientific trustworthiness of correctly signed sensor measurements**, while retaining all Phase V packet, temporal and admissibility guards.

## Bounded rules
1. One deterministic governing controller selects the best admissible action; otherwise HOLD.
2. Never count a repeated sensor ancestry as independent evidence.
3. Calibration, test seeds, failing counterexamples and action logs are append-only.
4. Each acceptance turn = 12.5% of the eight-turn phase; a failed gate earns no progress until corrected.
5. End the phase if proposed tests reach quorum, Byzantine adversaries or independent witness agreement: freeze at earned percentage and open a separate phase.
6. Signed packets, calibration challenges and simulation data are not field assurance; identify unproven assumptions every turn.
7. Phase V is a frozen baseline and shall not be rewritten.

**Phase VI begins at 0%. AETHER-121 local synthetic gate passed; tracker advances to 12.5%.**
