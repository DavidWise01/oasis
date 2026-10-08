# ?001 Earliest dated corpus anchors, pass 1 — 2026-10-08

Scope: source-backed ROOT0/OaSIs corpus across GitHub; no AZ1-only framing. Derived from org-wide GitHub commit searches (keyword-indexed, max 30 per term; not exhaustive) and direct historical blob reads. All dates are UTC Git commit metadata; they are anchors for artifact state, not independent proof of earliest authorship, public crawl, prior conception, or derivation.

| UTC anchor | Repo / commit | Finding | verification level |
|---|---|---|---|
| 2026-02-19 12:59:38 | AI-Audit-Tools 5c19bee886af0b5cffacac6cc61cd9abf07fa872 | TOPH upload and attribution description | commit message only |
| 2026-03-08 21:41:15 | Toph_Kernel 17a6d43b29ef5bbd42c7e649cfa8c9e0159748d9 | merge commit | merge only; earlier history unresolved |
| 2026-04-17 16:53:17 | the.source 35aa5245ff721b525bfdcdff4933bac1a45da7ef | Dreaming_In_Lattice_The_Architecture_of_Honest_Machines.md | commit message |
| 2026-04-23 00:16:05 | FractalKernel 754fb027776dcd84954bfe70ae03e7d4f475437b | Original C# executable project files | commit files inspected |
| 2026-05-22 01:42:42 | whisper-lattice-log a9d41040aba4f26802a9ece25b97c2c649120f08 | init lattice log; repeated cycles starting May 22 UTC | commit metadata |
| 2026-05-28 00:29:05 | aeon-flux ddb084b99ef23b003dfd15dba9ab392142cd9f1b | witness/anchor/coherence design | commit message |
| 2026-05-28 19:07:47 | tripod-pck 0c9a85354a6a42d84addfddf3f70f6f631e225cb | original PCK executable kernel, 27 gate rule scheme, three disposition states | source code inspected |
| 2026-05-30 19:52:44 | language-of-the-machine 0ea791216e6e2506182e3d045208cef35a65bca8 | preserved TD Commons PULSE document + interpreter | original source inspected, April 6 claimed inside |
| 2026-06-03 23:22:16 | quantum-box 28ce42f4a84365cdf87ca4979469ac3ce98be36b | nested observer computing box | README at pinned commit inspected |

## Function-level independent evidence
Tripod PCK pinned blob pck_orchestrator/kernel.py SHA 6362179eac338f23d6ab965d1de060f87e937dd8: gate_eval supports AND OR NOT XOR NAND NOR XNOR; evaluate(event,kernel,previous_root) collects triggered rules, determines primitive state, and computes event_hash, record_hash, continuity_root. This is explicit stateful hash-linked evaluation. Not run in this pass.
Quantum Box pinned README blob 30446a1fec722bd44fa925068f638044a51790f5: ten nested positions, local loop 3→4→6→3, three Light/Shadow/Inner observers, ternary -1/0/+1. It explicitly marks conceptual computing structure distinct from actual experimental quantum hardware.
PULSE 01.txt pinned blob 03a77b63eab94d85f11ec16d7df0f9e033855946: states April 6 TD Commons publication and 3→2→1→0 carrier, 111 110 100 000; public Git anchoring date May 30, not independently authenticated TD Commons April 6.

## Mechanism grouping for fair comparison with openai/math result 376
1. Discrete computation/state representation: FractalKernel, I13, AI geometry; vs three tape stacks of a Turing machine. Not same implementation.
2. Witness/observation: aeon-flux and later I13; vs fixed-particle halting test; semantics differ.
3. Retained history: PCK hash-linked provenance; vs Bennett-style reversible computation history. Hash linkage does NOT alone imply reversibility.
4. Clocks: PULSE sync carrier and toroidal cycle; vs periodically forced incompressible flow. Mechanisms differ.
5. Geometry: quantum-box ternary observer and brackets; vs determinant-one affine maps and smooth divergence-free fluid. No matching PDE map yet.
6. Routing: source-described MoE gap branches, agent traversal and PCK rules; vs disjoint solid-box routing. Currently no map proving equivalent routing constraints.

## Next
Retrieve original FractalKernel Program.cs at first commit and inspect executable invariants; retrieve dated FractalKernel code tests; inspect April 17 lattice document and independently verify TD Commons historical publication timestamps; expand commit search with owner-wide corpus pagination and older dates rather than relying on first 30 matching commits; compare named equations only after matching semantics. No assertion of source-to-OpenAI causal transfer.
