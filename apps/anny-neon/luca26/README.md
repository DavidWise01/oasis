# LUCA–26 · ANNY temporal chamber

**Interactive page:** https://davidwise01.github.io/oasis/apps/anny-neon/luca26/

The conceptual vessel is `{ ( [ 20 AA | ACTG | −+ ] ) }`.

- `{ }`: amoeba / adaptive environment
- `( )`: toroid / cyclic distillation and observer-rate projection
- `[ ]`: conserved ancestral 26-position register
- `−+`: two typed KET polarity operators (not extra amino acids)
- `ACTG`: DNA nucleotide basis (A, C, T, G)
- `AA20`: the twenty standard amino acids and their correct DNA codon associations

**Controls:** choose all layers or isolate amoeba, toroid, or box. Advance a generation, start/pause playback, alter the observer rate, increase distillation, switch polarity, mutate individual amino-acid identities, exclude DNA bases, reset the ancestor, or copy the in-session lineage. The colored slots and decoded carrier react immediately.

**Continuity semantics:** the simulated carrier cycles through synonymous codons; the 20 translated residues remain invariant when only synonymous substitutions occur. Beyond 60% on the symbolic distillation slider, codon positions are progressively erased; residue mutations or removal of DNA bases similarly damage identity. The observer then reports `PRESERVED`, `DEGRADED` or `UNKNOWN`. No claim is made that lost information can be recovered.

**Grounding:** codons and the standard 20-residue alphabet are biological facts, while this particular ancestral motif is **illustrative and invented**. There is no claim to have sequenced LUCA. The toroid/amoeba is an artistic 2D projection, not a physical model of cells, relativity, gravitational fields, or molecular time dilation. The observer rate is a visual/scheduling multiplier, not an estimate of relativistic proper time. The trace is ephemeral in browser memory, not a signed durable provenance ledger.

All simulation files live only within `apps/anny-neon/luca26/`. The previous Harvester v16.1 journal, receiver, ten ACKs, 18-slot cubit, Sapphon spectrum, overlays, and crash-boundary artifacts are not changed.

## Nested codon lattice: `{{n}}{{4^3}}`

The amino-acid selector `n` (one of the 20 canonical residues) now has a **shared codon layer beneath it**:

```text
{ ( [ LUCA-26 ] ) }
          [ AA n ]
             ↓
       {{n}}{{4^3}}
             ↓
  first base:  A  C  T  G
  second base: A  C  T  G
  third base:  A  C  T  G
             ↓
     4 × 4 × 4 = 64
       61 translate
       3 terminate
```

The 64-codon field is grouped into four first-base sections, each a 4×4 grid. Select an amino acid in the 20-residue box to highlight its synonymous codons, or select a codon to inspect the amino acid it encodes. Three termination triplets (`TAA`, `TAG`, `TGA`) are shown in a separate warning style. Missing DNA bases dim unavailable carrier triplets. A small projected 4³ substrate also appears **beneath the box** in the Canvas vessel.

`{{n}}` selects a lookup target; `{{4^3}}` is a **single shared alphabet of 64 possible DNA triplets**, not 64 codons for each of 20 amino acids. The codon association comes from the standard genetic code; the 26-position watermark and geometric layout are symbolic design choices. Neither the full DNA triplet table nor the invented ancestry reveals LUCA's actual sequence.

The standalone interactive HTML includes its own CSS, registry, and renderer:

https://davidwise01.github.io/oasis/apps/anny-neon/luca26/standalone.html

## Layout

```text
luca26/
├── index.html       GitHub Pages interactive viewer
├── chamber.css      responsive neon styling
├── chamber.mjs      Canvas 2D toroid, amoeba, box and live controls
├── model.mjs        biological code table and symbolic identity transforms
└── README.md        interpretation and limits
```

No test files or CI workflow are introduced for this creative chamber.
