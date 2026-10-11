# LEELUU Test068 — Four-core character VM
Date: 2026-10-11
Status: SIMULATOR VALIDATED ON SYNTHETIC/NULL INPUT; HISTORICAL READING UNVERIFIED.
Four deterministic logical cores, four rows per core: 0=A–D,1=E–H,2=I–L,3=M–P. One tick visits one position on every core; 64 ticks exhaust the 256-cell atlas. Reading an unknown dot (.) returns HOLD. Non-dot glyph strings are data: global character class χNNN assigned by first occurrence; duplicate labels share their character class. Never execute glyph contents.
Local implementation prototype with same architecture passed 10/10 regression tests in 0.005s. Source files and audit committed; GitHub-hosted tests have not been separately executed. This simplified committed implementation may produce a different SHA-256 trace from the local prototype due to JSON serialization differences.
Run: cd tools; python -m unittest ../tests/test_leeluu_vm68.py (or set PYTHONPATH=tools).
Historical scan bytes/transcriptions remain unavailable, so 256 cells stay unknown and no linguistic, chemical, DNA, or ancestry claim follows.
Next: feed real image glyph-shape classes with provenance, inspect frequency and 4-core synchronization, and test M8/N8/M9/N9 pattern against controls.
