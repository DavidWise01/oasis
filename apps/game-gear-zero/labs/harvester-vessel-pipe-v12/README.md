# Harvester v12 · 40-bit Vessel Pipe

**Status:** executable symbolic model. Standalone HTML in `index.html`. Built on the v11 carrier-motion and clamping system; the original v11 and prior versions remain separate.

## User's exact vessel pipe

```text
{{lv > . . . . . > 40 bits > . . . . 2^3 > 1 1 2 4 > 1 in , 1 , out > {{ix2}} , r1,g1,b1,bk1 }}
```

This notation is preserved literally. `lv` and `{{ix2}}` are **opaque symbolic tokens** awaiting user-defined semantics. They are not implemented as real instructions, arithmetic multipliers or physical components.

## Explicit experimental mapping (not frozen semantics)

- Input: five positions (`. . . . .`) each hold a byte, totaling **5 × 8 = 40 bits**, supplied as 10 hexadecimal digits. The entire 40-bit register is retained in each packet and exported receipt.
- Projection: four positions (`. . . .`) each occupy a **three-bit state**, giving `2^3 = 8` possible values per position, **12 projected bits** in total. For position i=0..3, the working sample is `q[i] = (inputByte[i] XOR inputByte[4]) & 7`. This uses the fifth byte as a mask; it is not lossless compression.
- Weighting: `[1,1,2,4]` provides a derived score `q0 + q1 + 2*q2 + 4*q3`, integer range 0–56. These are **provisional signal weights**, not prescribed physical forces or the user's final interpretation.
- Lanes: `r1`, `g1`, `b1`, `bk1` are four one-bit symbolic witnesses, each `q[i] & 1`. BK is the fourth channel, not renamed or silently discarded.
- Transport: **1 ingress / 1 verified egress per loaded packet**. No automatic transfer. The `IN` and `OUT` commands require `SECURED` v11 clamp, all nine v11 interlocks, docked finite stroke, acceptable velocity and holding-force margin, and no active rail fault. A new packet must be loaded for a new transfer.

## State machine

```
EMPTY -> LOAD -> LOADED -> IN -> IN_FLIGHT -> OUT -> COMPLETE
                              |                ^
                              + fault -> HELD -+ RESUME, only if interlocks restored
                                              + ABORT -> ABORTED, no egress
```

An attempted clamp release/reset while there is an occupied vessel pipe **does not release the clamp**. Loss of a required Hall rail or v11 interlock during transfer latches `HELD`. An explicit abort discards the modeled packet and generates an abort receipt with no output count. Duplicate input/output operations are rejected. Receipt history is bounded to the latest 96 records. Digest and receipt `hash` are **32-bit FNV-1a checksums for simulation consistency only, not secure signatures or tamper-proof provenance**.

## Run / tests

Open `index.html` in any current browser (no network required). For a full cycle:
1. Click **NEXT CLAMP STEP** to approach, then **DRIVE +128 / DOCK**.
2. Click **NEXT CLAMP STEP** five more times to pass ALIGN, ATTACH and the two distinct VERIFY ticks. Clamp should report `SECURED`.
3. Enter 10 hexadecimal digits, then click **LOAD 40 BITS**, **1 IN / SEND**, **1 OUT / VERIFY**.
4. Examine the retained input bytes, projected three-bit values, weighted score, color lanes, and signed ingress/egress receipts. Export JSON when useful.
5. For fault testing, load a second register, issue **1 IN**, then **OPEN HR11**. It enters `HELD` without an output. Repair the rail and return the clamp to the secured state before resuming, or **ABORT PIPE** and physically retract the clamp safely.

Verification: run `node tests/pipe.test.cjs` and `python3 tests/browser.py` with Python Playwright/Chromium installed. The deterministic pipe engine passed **16,406 assertions**, and the browser covered valid/invalid ingress, secure docking, the Hall fault, latched HOLD, abort, safe clamp release, JSON export, and mobile layout. The old v11 finite-stroke engine is embedded unchanged.

## Physical boundary

This is a **symbolic information pipe and control-state simulator**, not an executable physics law, a quantum process, magnetic field solver, physical harvester or matter-transport device. Its bytes, weighted score and color witnesses are intentionally dimensionless. The existing `1g*` in v11 remains a dimensionless balance proxy, not real gravity. The symbolic `40 bits`, `2^3`, `{{ix2}}` and `lv` do not independently establish physical transportation or conserved mass/energy.
