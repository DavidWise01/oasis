# LEELUU Test067 — Character i-pass baseline
Date: 2026-10-11
STATUS: SOFTWARE PASS; HISTORICAL TRANSCRIPTION NOT AVAILABLE

Each 16x16 cell is now a character address, rather than an atom role. Unknown transcription remains `.` (the user's open dot), and the inference pass allocates canonical character-class IDs (χ001, χ002...) only when a real input reading is provided. Repeated explicit readings reuse the same ID. A pair is scored only if **both** endpoints have real readings; adjacency alone does not imply grammar, bonds or semantic identity.

## Executed local benchmark
`python test_i67.py` — 6 tests run, 6 passed, 0 failed.
`python leeluu_i67.py` (no supplied glyph transcription):
- atlas addresses 256
- verified transcribed characters 0; unknown 256
- distinct inferred character classes 0
- possible axis-adjacent pairs 480 (=16x15 horizontal +16x15 vertical)
- observable two-character pairs 0
- C8-C9, A8-B8, K8-L8, M8/N8/M9/N9 unresolved (`.`)
- no physical identity, chemical or ancient ancestry finding.

## Test files
`tools/leeluu_i67.py` pipeline
`tests/test_leeluu_i67.py` regression
A future transcription file may contain any subset of canonical addresses mapped to independently observed glyph drawings/classes. Such labels must not be taken as historical letters until verified. This is a truthful null-input baseline, NOT a failed physical decoding and NOT proof glyphs are identical.

## Next
Extract source cell images and group shape-identical forms with provenance, then supply an explicit transcription; rerun i and measure repetition, n-grams, permutation patterns, and controls.
