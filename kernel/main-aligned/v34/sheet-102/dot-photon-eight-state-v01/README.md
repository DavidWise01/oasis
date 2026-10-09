# SHEET 102 — DOT ≡ PHOTON / 2³ Local State / Network Cost

Append-only specification for `OaSIs` following SHEET 101. This is a new **symbolic kernel constant** supplied by the user, not a claim that light is proven to behave like a computer packet.

> “the photon moves with each dot of time the dot is the photon and it carries a 2^3 state space with every single jump, it just follows the rules of networking costs and linear algebra”

## Canonical primitive

- **Identity:** `dot_t ≡ photon-token_t`. There is one carrier occurrence per logical time dot. The token remains one token as it moves; it does not split into eight photons.
- **State at every dot:** `S={0,1}³`, `|S|=2³=8`. Carry the **whole** vector `v_t=(v_000,...,v_111) in R^8` to every successor dot, not only the selected basis address.
- **One discrete jump, one logical tick:** `t_next=t+1`. This is an abstraction and is not equated to a measured Planck interval or propagation speed.
- **Network cost:** each permitted edge `e=(u,v)` has a finite, nonnegative `c_e`; `C_next=C+c_e`. Cost is a distinct scalar from the tick and need not equal elapsed logical time.
- **Linear transform:** `v_next=P_e v`, with `P_e` a chosen 8×8 transition matrix. This initial realization uses an invertible permutation `P_m`, `m=u XOR v`, with `(P_m v)[i XOR m]=v[i]`. Thus `P_m^(-1)=P_m^T=P_m`, and it preserves sum of components and squared Euclidean norm.
- **No state multiplicity inflation:** one logical photon token, eight carried **addresses**, zero packets cloned. Appending a new dot is advancing an event; it does not overwrite historical lineage.

In compact form:

`Phi_t = (dot_t, v_t, C_t, t)`

`Phi_(t+1) = (dot_(t+1), P_e v_t, C_t+c_e, t+1)`

The default demonstrator uses an 8-node **ring plus four opposite chords** (12 undirected edges) with deterministic positive costs `1+((3*min(u,v)+5*max(u,v)) mod 4)`. Dijkstra's algorithm selects a globally minimum-cost route; every successful edge traversal increments `tick` by exactly one. The graph is an implementation **example**, not an asserted physical network topology.

## Relation to SHEET 101

The previous architecture has eight physical silo domains `D0…D7`, one **separate logical aggregate `D8`**, 72 symbolic toroid addresses, 11 symbolic copper sheets per silo and 120 tracked packet identities. The carrier's 2³ components may be addressed against `D0…D7`, but **the eight local state components are not eight additional physical domains**; `D8` is not a ninth basis state. SHEET 102 is **a tested primitive and standalone visualization**, not yet spliced into the SHEET 101 live scheduler, clearance, or ACK kernel. Earlier sheets and negative tests are untouched.

## Verified WebAssembly benchmark

The real `kernel.wasm` is compiled from `kernel.c` (WASM32, freestanding C, no libc) and executed in Node. **1,209/1,209 assertions passed** across **64/64** start/target pairs, a total of **94 realized hops**, maximum **3** hops per route, and maximum **5** units of route cost. In every test, tick and hop counts matched; source→target state was one reversible XOR-permutation of the entire vector; the cost matched a second independent shortest-path implementation; initial full state `[1,2,3,4,5,6,7,8]` conserved sum **36** and squared norm **204**. Invalid addresses and retargeting were also checked.

The standalone SVG viewer contains the **actual embedded 2,360-byte WASM**. **Chromium rendered it with zero page errors** via Playwright `page.set_content`, since file:// and loopback navigation were blocked by this test environment's browser policy. It successfully stepped once, completed a route, reset, and displayed 8 basis components, 8 nodes and 12 links. The browser test does not validate actual external deployment, networking or literal photons.

## Rebuild / run

```sh
clang --target=wasm32 -O2 -fno-builtin -nostdlib -Wl,--no-entry -Wl,--export-all -Wl,--strip-all -o kernel.wasm kernel.c
node test_wasm.js
python build_viewer.py
python test_browser.py  # requires Playwright / Chromium
```

Open `index.html` as a standalone WASM/SVG visualization on a browser which permits local-file pages. It does not fetch remote scripts or binary files. The buttons select source and destination, take one dot step, finish a route, and reset the carrier. Its routing visualization is deterministic; it does not draw actual electromagnetic waves.

## Next integration gate

Before attaching this primitive to the eight-silo D8 aggregate, verify that the surrounding queue/scheduler and clearance invariants remain valid, that all 120 lane identities are preserved and no extra packet identities are created by the 8-state carrier representation, and that network costs are consistently defined across per-silo queue edges. Do not conflate eight carried basis states with eight separately transported packets.