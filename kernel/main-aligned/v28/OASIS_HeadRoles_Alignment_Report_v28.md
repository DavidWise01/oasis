# OASIS Head-Role Family Alignment — v28

## Decision

**Keep the family, but preserve the evidence tiers.**

The ten files share a reusable offline instrument template and the exact same embedded RH0/RH1 matrix pair. Only Attention Sink and Positional/Syntactic use that pair as their primary GREEN quantitative evidence; the other eight are AMBER constructed/conceptual fixtures.

## Tests

### Shared matrix corpus

All 10 files contain byte-equivalent parsed RH0/RH1 arrays: **PASS**

Matrix shape: **15×15**

Row-sum ranges:
- RH0: 0.9999 .. 1.0002
- RH1: 1.0000 .. 1.0003

### Attention Sink

Recomputed total mass landing on token 0:

**0.27006686 = 27.007%**

This matches the page's displayed ~27% result.

### Positional/Syntactic

Aggregating RH1 by relative offset `j-i` gives:

- dominant offset: **+1**
- aggregate mass at that offset: **1.4070**

### Induction

Constructed sequence:

`3 7 1 9 2 3 7 1 9 2`

Scored repeated-token cases: **4**
Correct match-then-copy cases: **4**
Copy score: **100%**

### Previous Token

The constructed 12×12 route has 11 predecessor rows at weight 0.9.

Important detail: row 0 sums to **0.1**, while rows 1..11 sum to **1.0**. So it is a routing fixture, not a normalized attention matrix for every row.

### Retrieval

- context length: 20
- needle index: 3
- query index: 19
- distance: **16**
- target weight: 0.98
- full constructed vector sum: **0.998**

Again, useful route fixture; not a complete normalized measurement.

### Name Mover

Supplied non-zero weights:
- Mary 0.82
- first John 0.10
- repeated John 0.04

Total = **0.96**, so v28 preserves it as an illustrative partial vector rather than pretending it is a normalized attention distribution.

### Successor

The source implementation is a seven-day cycle. Seven successor applications return to the starting day: **PASS**.

### Faithfulness / Coherence

Faithfulness's 0.86/0.34 labels are hard-coded illustrative values, so v28 keeps only `coincident | divergent`.

Coherence has a constructed EN/FR tag fixture. For query index 6 (EN), the prior same-language targets are exactly **[0, 1, 3]**.

## What falls out

The ten "heads" reduce usefully to three implementation stages:

`SELECT / ROUTE -> TRANSFORM / WRITE -> VALIDATE / BRAKE`

Examples:
- SELECT/ROUTE: sink, previous-token, retrieval, name-mover, positional
- TRANSFORM/WRITE: induction, successor
- VALIDATE/BRAKE: copy-suppression, faithfulness, coherence

This is a useful routing taxonomy for OASIS, but it is not a claim that every transformer has exactly these ten named heads.

## Authority

All ten fixtures resolve to HOLD. They can route or review evidence; none can authorize durable kernel state.
