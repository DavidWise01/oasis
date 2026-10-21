# Harvester v13 — Exact 40-bit Receiver Readback

Standalone, offline HTML in `index.html`. Preserves all v12 gyro, five-pulsar, torque, Hall, carrier, guarded clamp, and vessel-pipe engines while layering a new deterministic receiver experiment over the output gate.

## Canonical user notation — unchanged

```text
{{lv > . . . . . > 40 bits > . . . . 2^3 > 1 1 2 4 > 1 in , 1 , out > {{ix2}} , r1,g1,b1,bk1 }}
```

The meaning of `lv` and `{{ix2}}` is **not** assumed. This version experiments with **two software readback witnesses**, A and B, at the exit without declaring that `{{ix2}}` means multiplication, replication, or physical duplication.

## Why this upgrade

V12 kept the original 40-bit input in its packet, but its egress was checked using a digest and guard status rather than reading a distinct output register. Four three-bit states (12 bits) and the weighted 1/1/2/4 score cannot reconstruct an arbitrary 40-bit source. V13 explicitly compares **all 40 individual bit positions**.

## Data flow

```text
5 input bytes → 1 IN → preserved original 40-bit capture
                                ├── RX A (40-bit software register)
                                └── RX B (40-bit software register)
                                                 │
                              source, A and B must ALL match 40/40
                                         ┌───────┴────────┐
                                        pass             fail
                                         │                 │
                                guarded 1 OUT           HELD
                                exact hex receipt       no egress
```

- A verified egress receipt contains `sourceHex`, `receivedHex`, `readbackB`, bit-match count, test checksums and the modeled tick.
- Separate explicit controls flip any bit index **0 through 39** in A or B for fault injection.
- A mismatch instantly latches V12 `HELD` with **zero added egress**. Recovery requires explicit **RESTORE READBACK** and **RESUME HELD**, with all prior V12 clamp/Hall/force interlocks still passing.
- Flipping the **same bit in both receivers** is rejected because source-to-A and source-to-B are independently compared; agreement of corrupted receivers does not count as integrity.
- `ABORT` produces no output and does not fabricate a delivered register. Receipts are capped at 96 per audit stream.
- The original 5×8=40-bit input, 4×3-bit projection, 1/1/2/4 weighting, and `r1/g1/b1/bk1` witnesses are unchanged.

## Tests

Run from this folder:

```bash
node tests/integrity.test.cjs
node tests/v12-regression.test.cjs
python3 tests/browser.py
```

Verified locally: **131,093 new deterministic assertions**, **16,406 inherited v12 assertions**, desktop Chromium with valid exit, A/B bit faults including equal-position common corruption, held/resume/abort, JSON export, and mobile rendering. Source engine: `engine/exit-integrity.js`.

## Scope and limitations

This is a software information-integrity experiment, **not** a physical transporter or quantum device. The two receiver buffers are constructed from the same source in memory, so the test does **not** establish independent hardware witnesses, electrical error correction, or physical lossless communication. It demonstrates an exact equality gate within this deterministic simulated model. The audit uses test-grade 32-bit FNV-1a checksums, **not cryptographically authenticated or tamper-proof signatures**. `{{ix2}}` remains an unresolved symbolic operator. The earlier `1g*` is a unitless control balance indicator, not actual acceleration or generated gravity.
