# P3.58 — Integrate complete SHA-256 chain verification into 3-of-4 witness acceptance

2026-10-09. This integrates the P3.55 canonical hash chain verifier and P3.57 authenticated witness quorum. It does not accept a quorum of signatures until every chain link and payload is validated, including retained trusted prefix ancestry. Three envelopes, 1440 records each.

Node v22.16.0 local test PASSED 24 assertions; tests include corrupted middle records, shortened history, insufficient signatures, interrupted/resumed history, conflicting legitimate branch, and acceptance of a valid continuation. Two competing three-of-four quorums can both be approved independently if shared witnesses equivocate. Persistent anti-equivocation state, intersection accountability and a fork-choice/finality protocol are necessary before claiming consensus. A process losing all external trusted checkpoint state cannot detect independent self-consistent chains. Tests use ephemeral keys; do not commit secrets.

Next P3.59: enforce signed no-double-vote rule per witness/epoch and generate equivocation evidence and reconciliation protocol.