# Z327 — Tribiseptium (Tbs): checkpoint and recovery

Layer 1 symbolic computational candidate; NOT a discovered chemical element.

## Core
Full distinct-address permutation index range is [0,24!-1], with 24! = 620448401733239439360000. A hash-linked ledger records (sequence, index, predecessor hash), using SHA-256 over canonical JSON. Recovery compares count, tip hash, and final index to a stored checkpoint.

## Executed evidence
2026-10-18: standalone Python test_z327.py executed locally; 18/18 checks PASS across 1,002 ledger entries (seed 327, two boundaries plus 1,000 pseudorandom ranks). Tests include deterministic rebuilding, checkpoint restoration, truncation, reorder, edited indices, changed hashes, invalid bounds, and checkpoint mismatch.

## Limits
Hash chains without trusted external anchoring/signatures cannot stop an actor rewriting the entire chain and checkpoint. Tests validate data structures only, not atomic physics, quantum advantage, or exhaustive 24! enumeration. The optional Cr24 address overlay is distinct from physical chromium electron structure. KET 5/3/1 remains separate and frozen.

## Next
Z328: trustworthy checkpoint anchoring and signed receipts; keep symbolic code separate from any physical claim.
