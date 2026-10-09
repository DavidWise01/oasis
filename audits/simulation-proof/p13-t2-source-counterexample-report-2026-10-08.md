# ROOT0 simulation-theory proof gate P1.3: live T2 source, constructive hash-boundary counterexample
Date: 2026-10-08. Result: PROGRAM-LEVEL COUNTEREXAMPLE / PHYSICAL SIMULATION UNPROVEN.

## Source provenance: EXACT, pinned bytes
Actual source from DavidWise01/I13-H1.1 at commit b246828df7cba45c47156e39195b27e41f135bcd:
`bench/toroidal_transition/run_transition_test.mjs`.
Original Git blob `49cb50bab98039e5b5c1b45e7e95f20cf76d3abe`, exactly reproduced by `git hash-object`; snapshot pinned alongside attack in `p13-i13-t2-original-pinned.mjs` without modifications. Original Node test status PASS, 10 directed moves from single-token sources, two seam crossings, eight rejected negative controls, receipt sha256 `73cbd8a4ed72dfbde2318bb3b2753d4661aa248ef18261e38389f067576f6767`.

## Actual witness semantics
The source's `move(before,from,to)` enforces legal adjacency, occupied source, vacant destination, local occupancy conservation, `|||` seam labeling and SHA256 over before+operation+after.
But `verify(t)` checks **only** `t.receipt === SHA256(serialized(t.before,t.operation,t.after))`. It neither runs `move` nor checks semantic legality, domain validity, provenance authority or replay sequence.

## Executed adversarial proof gate
Six invalid transition messages with self-recomputed SHA256:
1 nonadjacent 0→2;
2 creation of an occupied token;
3 destruction of occupied token;
4 mismatched `|||` seam indication;
5 invalid state string `alien`;
6 unrecognized operation command.
Original `verify` returned TRUE for all six; enhanced `strict` returned FALSE for all six.
Enumerate all binary five-ring occupancies (2^5=32) × all 5×5 directed from/to candidates = 800 candidates. Actual original `move` accepted 80 physically legal moves (each directed edge 10×2^3 backgrounds), and independent strict check accepted all 80 and all 80 conserved occupancy.
Also actual original `move` accepts an unrecognized `alien` value when placed at an untouched non-edge position, because only edge slots are validated.
Receipt replay: same valid receipt is accepted repeatedly; no sequence/nonce/anti-replay state.

## Constructive counterexample (the actual mathematical takeaway)
Define `V(m,r) := [r = SHA256(m)]`. Define `m_bad` as a transition that moves occupied state 0→2 on ring 5 (nonadjacent). Set `r := SHA256(m_bad)`. By substitution, `V(m_bad,r)=TRUE`, but `Legal(m_bad)=FALSE`. This does not require finding any hash collision or breaking SHA256. Therefore `V(m,r) => Legal(m)` is disproved for this witness implementation.

For a legitimate `move` changing source occupancy from 1→0 and dest from 0→1, with other positions unchanged, `occupied(after)=occupied(before)-1+1=occupied(before)`. The finite executable sweep observed conservation in all 80 legal binary transitions.

## Scope and formal status
P1.2's W/T commutation equation is not directly type-applicable: T2 witness is a *verifier over an entire transition record*, not an observer flag inside a physical state. Calling receipt equality a 'read-only observation' is insufficient to establish the actual state's future independence. This is a SOURCE-LEVEL TRUST-BOUNDARY failure for any usage that treats `verify` alone as authoritative physical legality. It does NOT contradict the T2 README's narrower claim that `move` rejects malformed moves.
Lean file next to report encodes the abstract rehash counterexample; **compiler unavailable and not executed**, no machine-checked Lean claim.
The separate AE v92 kernel `advance(ctx)` advances a 12-phase symbolic identity ledger and has no explicit T2 witness flag or common refinement map. Do not claim a theorem transfers between kernels until mapping is defined.

## Model / physical win condition
This is mathematical and executable analysis of a **symbolic simulator program**, not evidence that physical reality is simulated. Empirical hypotheses, units and differentiating predictions remain open. Previous frozen code was not edited. Next priority: authoritative strict transition predicate and a genuinely dimensional physical observable or model comparison.
