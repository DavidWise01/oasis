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

## Three-strand zipper crown · `3 × 20` above the box

The user-facing chamber now places a **60-observation symbolic zipper** over the 26-position LUCA box, with its existing shared 64-codon field underneath.

```text
             α [20 AA]  ← live decoded carrier
             β [20 AA]  ← symbolic reference strand
             γ [20 AA]  ← symbolic reference strand
               ╲ | ╱
          ZIPPER (20 teeth)
               ↓
       [ 20 merged / HOLD ]
               ↓
          [ LUCA-26 ]
               ↓
        {{n}}{{4³}} = 64
```

- The top register has three ordered *lanes*, each with 20 positions: `3 × 20 = 60` symbolic observations, merged position-by-position into **20 outputs**, not 60 additional amino-acid species.
- **α** reads the current transformed LUCA-26 decoded residue positions (including mutations and missing information); **β** and **γ** are initially copied symbolic reference lanes. Click a tooth to introduce/remove a local variation.
- The zipper slider and `− OPEN 1`, `+ ZIP 1`, `↣ ZIP ALL` controls move through the 20 physical-looking symbolic teeth.
- `β offset` / `γ offset` deliberately shift the apparent address/temporal alignment; `◎ ALIGN CLOCKS` resets offsets to zero without erasing mutations.
- `3/3` requires all three visible residues to match the pinned ancestral position. `2/3` permits symbolic two-vote quorum *only when at least two match the pinned ancestral position*. Unclosed teeth remain `OPEN`; disagreement in a closed tooth gives `HOLD`.
- The Canvas view also renders a three-strand crown **above** the inner box, while the pre-existing 4³ codon lattice remains **beneath** the box.
- These are educational/symbolic information-flow and temporal-alignment analogies. Three copied strands **do not constitute three independent historical witnesses**, majority voting does not restore unknown biological ground truth, and natural ribosomal translation does not involve a universal three-protein-strand zipper of twenty amino acids.

This feature adds no unit-test suite or workflow changes, per the user's direction.

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

## Neon-10 symbolic practice chamber

**HTML:** https://davidwise01.github.io/oasis/apps/anny-neon/luca26/neon.html

Exact user-provided unbalanced glyph:

```text
{1.2}{(3|4)(5|6){7.8}(1|0)
```

Balanced display (the only structural repair is a final brace):

```text
{1.2}{(3|4)(5|6){7.8}(1|0)}
```

- Inner first pair: `{1.2}` → electron addresses E01 and E02 (physical n=1 shell).
- Outer four pairs: `(3|4)`, `(5|6)`, `{7.8}`, `(1|0)` → E03–E10 (physical n=2 shell).
- The last `(1|0)` contains the original **two literal glyphs** `1` and `0`, bound by explicit address metadata to E09 and E10 for this visualization; never silently convert the characters to numeral `10`.
- This gives **5×2 = 10 symbolic electron addresses**, which overlays the real neutral Neon shell occupancy of **2+8**, and ground-state electron configuration `1s² 2s² 2p⁶`.
- Click a pair or electron, fold/unfold the groups, change the illustrative observer rate, pause motion, and apply display-only distillation to remove labels. All 10 electron positions remain represented; information-loss controls never mean a real electron has vanished.
- These are symbolic KET grouping and occupancy *analogies*, not atomic orbitals, or actual relativistic time dilation.

The page is a self-contained `neon.html` with no external JS or CSS dependencies. The LUCA-26 zipper, 26-register, underlying 64-codon lattice, and main ANNY Harvester are not modified.


## Radon-86 · Six-shell interactive practice

**Single-file HTML:** https://davidwise01.github.io/oasis/apps/anny-neon/luca26/radon.html

This intentionally extends the previous **Neon-10** symbolic vessel without changing the original Neon file or the LUCA-26 code:

```text
Ne-10 seed:
{1.2}{(3|4)(5|6){7.8}(1|0)}

Radon symbolic outer-shell extension:
{{n3:9×2}}{{n4:16×2}}{{n5:9×2}}{{n6:4×2}}

Physical neutral Rn shell occupancy:
n1=2 n2=8 n3=18 n4=32 n5=18 n6=8

Symbolic two-position gates:
1 + 4 + 9 + 16 + 9 + 4 = 43 gates = 86 addresses
```

The standalone HTML contains **86 selectable electron markers**, six concentric shell rings and shell selectors, all 43 paired gates, global fold/unfold, fold-all, clock-rate visualization, and label-distillation (which never removes physical electrons). Gates 1–5 retain the original Neon glyphs, including `1|0` as literal glyph characters rather than a decimal conversion. Shells 3–6 gain indexed pairs `E11|E12` through `E85|E86`.

**Physical data:** radon has atomic number 86 and electron configuration `[Xe] 4f¹⁴ 5d¹⁰ 6s² 6p⁶`. The shells contain 2, 8, 18, 32, 18, and 8 electrons. See the [NIST atomic data](https://physics.nist.gov/PhysRefData/Handbook/Tables/radontable1_a.htm) and [Royal Society of Chemistry entry](https://periodic-table.rsc.org/element/86/radon).

The page's **separate Rn-222 nuclear panel** shows alpha decay `²²²Rn → ²¹⁸Po + ⁴He` and the expected population remaining after elapsed time `t`:

```text
remaining_fraction = 2 ** (-t_days / 3.8235)
```

This is an ensemble expectation, not the decay time for one atom; after actual nuclear decay the product is polonium, **not** a Radon atom retaining the same electron structure. The half-life and alpha radiation are sourced from [EPA radon information](https://www.epa.gov/radiation/radionuclide-basics-radon) and [NCBI/ATSDR toxicological data](https://www.ncbi.nlm.nih.gov/books/NBK158787/table/T23/).

Neither the animated shell rings nor the 43-gate KET structure are literal electron trajectories, nuclear dynamics, or accepted atomic notation. The page uses no radioactive source or physical apparatus. No unit-test suite was added.

