# OASIS Corpus A→Z→A Alignment — v31

## Decision

**Keep, but split the exact construction from the interpretation.**

The source contains a real deterministic corpus snapshot and a real closed traversal. The stronger "the corpus is literally a palindrome / fractal / every part reseeds the whole" language is interpretation, and the source itself labels that distinction honestly.

## Snapshot checks

Embedded repository names: **859**

- first: `0root-provenance`
- last: `zoolander`
- duplicate names: **0**
- case-insensitive alphabetical order: **PASS**
- raw Unicode/code-point alphabetical inversions: **7**
- snapshot SHA-256 (`UTF-8 names joined by newline`):
  `19fcc9ce5a3ee8488d2709f794ed9e1edf83c3c8674824343e1e73849001fa6d`

The raw-order inversions are capitalization effects; case-folded order is monotonic.

## What "palindrome" actually proves

The source traversal explicitly goes forward A→Z, then returns Z→A.

For the embedded snapshot I constructed:

`repos ++ reverse(repos)`

- length: **1718**
- equal to its own reverse: **PASS**

So the **round-trip traversal is exactly palindromic by construction**.

That is different from saying the forward repository list is itself a palindrome. v31 formalizes the round-trip theorem generically and keeps the corpus-level metaphor separate.

## Live-data correction

The page statically embeds all **859** names.

Its one GitHub fetch requests only:

`https://api.github.com/users/DavidWise01`

and reads `public_repos`.

It does **not** fetch the live repository-name list. Therefore the page contains:
- a hard-coded name snapshot,
- plus a live count probe.

v31 records the snapshot as a receipt rather than calling the names "live."

## Self-similarity correction

The nested renderer uses:

- horizontal scale = **0.32**
- vertical scale = **0.34**

Because those scales differ, each nested lens changes aspect ratio by:

`0.32 / 0.34 = 0.941176471`

per level.

So it is **recursive nesting**, but not exact Euclidean self-similarity of the lens geometry.

## What survives

Useful substrate:

`snapshot -> ordered traversal -> reverse traversal -> return-to-origin`

plus the general constructor:

`roundTrip(xs) = xs ++ reverse(xs)`

The "every part is a seed for the whole" claim remains a conceptual hypothesis until a reconstruction procedure can actually rebuild the corpus from one part.

## Authority

The entire v31 fixture remains HOLD-only and does not alter Root, durable finality, or verified truth.
