# OASIS Attention Geometry / Null-Audit Alignment — v29

## Decision

**Keep this batch. The Observatory is the strongest artifact.**

The family contains useful exact math and good self-correction. The most important result is that the later Observatory explicitly catches an earlier curvature overclaim.

## Hourglass

The live fixture implements:

`Q·K / sqrt(d) -> temperature-softmax -> normalized weights -> weighted value blend`

For the supplied query and four keys:

- weights sum to 1 at every tested temperature: **PASS**
- tested temperatures: 0.05, 0.35, 1.0, 2.0
- entropy increases as temperature increases: **PASS**
- winning key remains K0 in this fixture: **PASS**

v29 therefore treats the raw dot product as a **score**, not the final prediction/output.

## Mesh / Tail

The modeled causal distribution was reproduced exactly.

### Mesh N=32
- max row-normalization error: `2.220e-16`
- sink is row argmax: **32/32**

### Tail N=44
- max row-normalization error: `2.220e-16`
- sink is row argmax: **44/44**

Tail query 32:
- sink mass: **0.595924**
- top-5 mass: **0.847801**
- entropy: **2.413346 bits**
- effective support: **2.664794 keys**

These are properties of the deterministic modeled fixture, not extracted-network telemetry.

## Attention Geometry

Exact source algorithm reproduction:

- tree: effective dimension **6.154957**, negative-eigen mass **3.2294%**
- grid: effective dimension **1.881288**, negative-eigen mass **4.8133%**
- shuffled: effective dimension **21.653184**, negative-eigen mass approximately **1.346e-16**

The useful part is the MDS/Isomap-style diagnostic. v29 does **not** preserve the stronger statement that negative eigenvalues alone prove a meaningful hyperbolic hierarchy.

## Observatory — strongest fallout

Exact source metrics reproduced under Node:

### BERT head 0
- effective dimension: **4.914495**
- negative mass: **10.2172%**
- shuffle-null mean: **18.3142%**
- top-3 coherence: **72.31%**
- persistence: **[11, 9, 4]**
- source verdict: **ARTIFACT**

### BERT head 1
- effective dimension: **7.823497**
- negative mass: **8.5807%**
- shuffle-null mean: **12.9647%**
- top-3 coherence: **50.13%**
- persistence: **[15, 2, 1]**
- source verdict: **ARTIFACT**

The Observatory's policy is strict: observed curvature must exceed **1.4×** its shuffle-null mean. Neither supplied real head passes.

That is the main thing that falls out:

`interesting statistic != structure`

until it beats a relevant null.

## Geometry Synthesis

Exact source target reproduced:

- tree = 0.09
- noise = 0.52
- effective dimension = **30.545859**
- negative mass = **3.2527%**
- top-3 coherence = **15.57%**

At tree=0.09, noise=2.0, negative mass jumps to **29.85%**, supporting the source's warning that noisy distance estimates can inflate this statistic.

## Rounded Sink receipt

The uploaded Attention Sink page carries the same H0/H1 matrix pattern as the Observatory, but rounded more coarsely. Across both heads the maximum absolute cell difference is **0.00005**.

So v29 treats it as a **rounded duplicate receipt**, not as an independent evidence source.

## Kernel alignment

The new durable discipline is:

`metric -> null control -> candidate interpretation -> current truth gate`

Never:

`pretty geometry -> verified physical/architectural truth`

All new attention artifacts remain HOLD-only at the durable authority boundary.
