# Lagado Test039 — Prescribed Six-Operant Routing: Test Before Expansion
Date: 2026-10-10
STATE: EXECUTED / MASS_CONSERVATION_PASS / ORIGINAL_GRAPH_UNCHANGED / SIGNED_ROUTE_PERFORMANCE_NOT_DISTINCTIVE
Parent: audits/lagado-six-operant-connected-vector-paths-v38-2026-10-10.md

## Frozen inputs
Source 256=208 active+42 reserve+6 provisional operants. Frozen 208 active nodes, 382 adjacent grid pairs, 109 original similarity bonds; inherited Test024 center/cortex gates and Test037 assigned six port addresses A5,C2,L1 (left - + -) and A12,C15,L16 (right + - +). Do not change edges or infer historical inscriptions.

## Prescribed operator, rather than pattern matching
The operants specify a period-six routing schedule - + - + - +. At each tick, retained probability 1/2 stays at each node; another 1/2 distributes on EXISTING bonded neighbors with normalized weights. Uniform W=1; cortex W=2^(-|gate_i-gate_j|); proposed controller W=cortexW * 2^(sign_phase * (col_j-col_i)), using horizontal grid columns and ±1 sign; vertical edges neutral. Factor 2 is experimental engineering parameter, not a historical/physics constant. Nonactive operant port inputs are *initial probability on their two adjacent active sites* and **not newly created communication edges**.

## A7 propagation through the previously existing bridge
A7 -> A8 -> A9 -> A10 supplies earliest possible left -> center -> right in 3 original bonds.
Right side means source columns 10..16; ticks measured in discrete simulation steps.

| Mode | t3 | t6 | t8 | t12 | t24 |
|---|---:|---:|---:|---:|---:|
| Uniform | 3.1250% | 14.5671% | 20.7689% | 29.7542% | 44.7604% |
| Cortex | 2.0833% | 10.7060% | 15.9987% | 24.4741% | 40.0113% |
| Cortex+sign operants -+-+-+ | 1.6667% | 12.1842% | 17.7286% | 26.5514% | 42.5249% |

Signed routing changes right-mass by +2.0773 percentage points versus cortex-only at tick12, but -3.2028 percentage points versus uniform. Normalized outgoing flux conservation holds to numerical error (<1e-11) for all tick0..24 and simulations; zero new graph edges.

## Exact alternative phase test
All 20 possible length-six schedules containing exactly three '+' and three '-' were scored at predeclared tick12 A7 right mass. Prescribed -+-+-+ ranks **9 of 20** (higher is better). Mean of all 20 is **25.6759%**. Post-hoc best ---+++ gives **34.3533%**, which is optimization on the same example and is NOT independent confirmation. Nothing here shows a distinct advantage of -+-+-+; do not promote.

## Original six-port reachability
The three provisional LEFT operants A5, C2, L1 each touch two existing left active sites in disconnected graph components with no path to any center/right atom. Injecting a unit split between those two active neighbors yields exactly **zero right and center mass at tick12 and tick24 for ALL three routing policies**. RIGHT-side ports A12/C15 share contacts with the already known 18-node bridging component but right-originated injection cannot substantiate LEFT-to-RIGHT routing; L16 injects into right-only isolated sites. All connectivity facts remain unchanged under positive reweighting.

## Artifacts and QA
Executable Python file build_lagado_routing_v39.py reads only frozen v22/v24/v37 CSV inputs, asserts 208/382/109/6 and original six labels, verifies 20 exact orders, 3 modes, six port inputs, mass conservation, A7 at tick3, disconnected left-port reachability. CSV outputs: lagado_routing_v39_A7_traces.csv, lagado_routing_v39_20_phase_orders.csv, lagado_routing_v39_six_port_inputs.csv; JSON summary; ASCII state and Markdown technical report.
Deterministic 12-file ZIP lagado_routing_v39_test_bundle.zip SHA-256: 095e9033f0ae119a8548e43ec6dce1a213bda24c1ca23d517bcc47669995dcae. ZIP integrity and per-member manifest hashes PASS; rebuilding twice produced identical archive digest. No retired wrapper written to new derived text. The original source engraving and external-archive lower-half replication limitations are unchanged.

DECISION: Signed controller executes and redistributes probability, but cannot repair disconnected inputs without new, explicitly labeled interfaces. No unique efficient phase schedule, no evidence of physical/bio historical code. TEST-FIRST verified; hold further routing product expansion.
