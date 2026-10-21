# Harvester v15 — Sequenced Packets, Receiver ACKs and Anti-Replay

**Offline:** open `index.html` in a browser. No server or dependency is required for the visualization. The pure model is in `engine/sequenced-transport.js`; deterministic Node tests are in `tests/`.

## What v15 fixes

V14 modeled two independent *software* paths A and B, each transporting five bytes of the original 40-bit register, with delays, missing bytes, corruption and explicit retransmission. It did not require separate per-byte acknowledgement or reject an old packet that arrived after a newer attempt had started. V15 fixes that without modifying the nine earlier embedded models.

- **Transfer ID:** starts at `TX-1` and increments on each new `1 IN` in the same simulation session. Clearing the register preserves the monotonically increasing ID and still processes outstanding old wire traffic as stale. Resetting the entire simulator begins a new session.
- **Packet identity:** every frame is tagged `(transfer ID, lane A/B, attempt, byte index)`. An attempt has indices 0–4 in each lane. A retry begins a new attempt, resetting that lane's receiver and ACK register.
- **Independent ACK delivery:** receiver sends a simulated ACK two model ticks after receipt of each byte. A is complete only with five ACKs for its *current* attempt; same for B. A dropped ACK leaves five bytes at the receiver but still blocks output.
- **Stale packet and ACK rejection:** old-attempt packets and ACKs are left in the modeled wire so they can arrive late; they are recorded as rejected and never change the current receiver.
- **Replay rejection:** manually replay an already accepted byte on path A or B. The identity is recognized as seen; it cannot issue a second ACK or mutate the register.
- **Exact 40-bit egress:** both receivers must obtain and acknowledge their own five bytes **and** both full 40-bit outputs must match the original captured source. No missing information is invented by the `2^3` projection, either receiver's buffer or old packets. `1 OUT` creates exactly one matched receipt.
- **Fault safety:** a dropped packet, corrupted byte or missing ACK yields `HELD` (zero new egress). Repair requires explicit clean retransmission from the retained sender. If the sender copy is discarded, a retry is denied; a latched clamp still requires safe retraction as in v11.

## Original user grammar (unchanged)

```text
{{lv > . . . . . > 40 bits > . . . . 2^3 > 1 1 2 4 > 1 in , 1 , out > {{ix2}} , r1,g1,b1,bk1 }}
```

`lv` and `{{ix2}}` remain uninterpreted. Two software routes and ACKs test a potential transportation control architecture but do not define those symbolic operators. The four 3-bit positions and `1,1,2,4` weights remain diagnostic and cannot losslessly encode an arbitrary 40-bit register alone.

## Live experiment

1. **NEXT CLAMP STEP** → **DRIVE +128 / DOCK** → five further **NEXT CLAMP STEP** presses until the clamp reads `SECURED`.
2. **LOAD 40 BITS** (ten hex digits) → **1 IN / SEND**. The transfer gets its own `TX-N` number.
3. Advance time using **DELIVER +16 TICKS**. A receives frames earlier than B by default, and ACKs arrive two ticks after each frame. Verify `5/5` on both paths and `5/5` ACKs each before **1 OUT / VERIFY**.
4. Try **INJECT DUPLICATE A**: the protocol logs `REPLAY_PACKET_REJECTED`; the receiver stays unchanged.
5. Clear the register and choose **LOSE ACK #2** for B. Send again; B can display `5/5` received with only `4/5` ACKs. **1 OUT** enters `HELD` and cannot fabricate receipt. Restore normal ACK mode, **RETRANSMIT PATH B**, advance ticks, **RESUME HELD**, then **1 OUT**.
6. For a delayed-stale-packet experiment, set a long delay on B, retry B with a short delay before the first batch arrives, then advance beyond the old scheduled delivery. `STALE_PACKET_REJECTED` appears in the bounded audit log.

The UI displays byte and ACK counts, transfer ID, path attempts, stale/replay reject count, plus existing Hall/clamp/gyro/ground, scope, ASCII and JSON/TXT/PNG exports.

## Test record

```bash
node tests/sequenced.test.cjs
node tests/v14-dual-path-regression.test.cjs
node tests/v13-integrity-regression.test.cjs
node tests/v12-pipe-regression.test.cjs
python3 tests/browser.py
```

Verified locally: **16,423 v15 protocol assertions**, **32,946 inherited v14 assertions**, **131,093 inherited v13 assertions**, and **16,406 inherited v12 assertions** (total **196,868**). Chromium desktop and mobile checked ACK loss, failed early output, replay rejection, lost-byte HOLD, explicit retry, matching egress, duplicate output block, discarded sender, export, and mobile controls. Nine previously embedded source engines are text-identical to v14.

## Reality / security boundary

All queues, network timing, bytes, ACKs, simulated Hall rails and motors exist in one client-side browser. It is not physically independent transport, real Hall-effect hardware, gravity or teleportation. ACKs are **simulated receiver events**, not signed messages from an independent computer. The receipt chain uses 32-bit FNV-1a for reproducible **checksums**, not cryptographic authentication. A malicious or compromised runtime could fake all of this. The `1g*` metric remains a **dimensionless** balance indicator; the user-specified 29.75 km/s display is not a measured physical speed.

Previous v14 is preserved as a separate executable. No upstream engine is overwritten.
