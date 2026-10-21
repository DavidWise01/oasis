# Harvester v14 · Dual-Path 40-Bit Byte Delivery

**Run:** [live lab](https://davidwise01.github.io/oasis/apps/game-gear-zero/labs/harvester-dual-path-v14/) | [offline self-contained HTML](./index.html) | [pure transmission engine](./engine/dual-path.js). The previous [v13 exact readback lab](../harvester-lossless-readback-v13/) is preserved.

## Literal vessel pipe

    {{lv > . . . . . > 40 bits > . . . . 2^3 > 1 1 2 4 > 1 in , 1 , out > {{ix2}} , r1,g1,b1,bk1 }}

The exact symbols `lv` and `{{ix2}}` remain undefined. Software paths A and B are a routing *experiment*, not a newly asserted interpretation of `ix2`.

## Change from v13

V13 compared two receiver buffers that were initialized directly from a sender copy. V14 implements **two independently scheduled software paths**. The original 40-bit input becomes five separately receipted 8-bit packets on **each** path, with independent delays (default A=2, B=6 modeled ticks), fault mode and selected 0–39 fault bit. Output is blocked until both paths have actually delivered all five bytes and match the original 40-bit source exactly. The prior Hall, clamp, torque, vessel and 1g* engines are retained.

    SOURCE 5 × 8 = 40 bits → 1 IN → PATH A (5 queued bytes) ─┐
                                  └→ PATH B (5 queued bytes) ─┤
                    receiving: 40/40 A AND 40/40 B AND live clamp interlocks
                                  └─ match → 1 OUT; else HELD

Per-path modes: NORMAL (five intact bytes), DROP (one selected byte never delivered), FLIP (one bit in a selected byte corrupted). Arrival timestamps are deterministic, and receipts record the lane, attempt number, byte index, delivery, loss or corruption. No missing byte is inferred from the twelve-bit color/weight projection. A missing or corrupted path requires explicit retransmission from the sender's **retained** original, which schedules five fresh packets. `DISCARD SENDER COPY` prevents retry. The source reference still remains available for auditing/verification, not as an unauthorized reconstruction path.

## Controls and failure behavior

First secure the Harvester clamp using its existing v11 motor/Hall interlocks. LOAD the 10-hex-digit register, then 1 IN. Use +1 or +16 transport ticks to deliver packets. With early 1 OUT, a path incomplete or corrupted, the pipe enters HELD with **no new output**. After valid retransmission and arrival, RESUME HELD followed by 1 OUT; this creates one matching output receipt. Repeated 1 OUT never duplicates the receipt. An aborted transfer emits no egress. Receiver fault toggles are still available; `RETRANSMIT BOTH PATHS` replaces v13's instant-memory repair.

## Tests

Run `node tests/dual-path.test.cjs`, `node tests/v13-integrity-regression.test.cjs`, `node tests/v12-pipe-regression.test.cjs`, and `python3 tests/browser.py` from this folder. Local reference passes: **32,946 new v14 assertions, 131,093 v13 readback assertions, 16,406 v12 assertions**. Chromium desktop/mobile passed clamp-to-egress, staggered arrivals, missing-byte HOLD, retry from retained source, no fabricated data after discard, output counts, and JSON export.

## Limits

Both simulated routes live in one browser; this is independent queuing/fault scheduling **in software**, not genuine physically separated network links or Hall hardware. All receipts use a test-grade 32-bit FNV-1a checksum, *not* secure signatures. Nothing here demonstrates an actual transporter, a physical magnetic clamp, gravity generation or quantum teleportation. The ring's 1g* indicator is a dimensionless balance proxy, and 29.75 km/s is the original user-selected visualization label.
