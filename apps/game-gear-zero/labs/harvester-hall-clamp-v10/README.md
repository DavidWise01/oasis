# HARVESTER v10 · Seven-slot Hall witness / symbolic clamp

Standalone offline HTML: `index.html` (all engine scripts embedded, no external dependencies).

Canonical transporter: `gyro1direction3brace6thrust6{{x^2y^2z^2}}6brace3direction1gyro`

- CARRIER = adjacent BRACE6 + THRUST6 stages. It carries a distinct CLAMP toward the VESSEL.
- VESSEL symbolic core = `{{x^2y^2z^2}}`.
- HARVESTER = CARRIER + CLAMP + VESSEL.
- Every instrumented vector uses `{{-+000+-}}`: 7 slots, signed pole placeholders and three virtual Hall samples.

## Inherited model

V8 remains unchanged. Five pulsars `v0,w0,x360,y360,z720`, CCW outer carrier (29.75 km/s label), CW bearing, CCW sun, modeled reaction torque and energy/momentum ledger, sea-cable return and symbolic black-hole stress/momentum sinks all remain untouched in the original pure JavaScript blocks. No claim of actual 1g gravity; `1g*` is dimensionless model balance.

## New deterministic witness overlay

- 19 canonical rails HR01–HR19.
- HR01–HR13 derive 39 virtual samples from v8 model signals.
- HR14–HR19 are geometry-only, 18 positions reserved, with null rather than fabricated sensor readings.
- H0 = normalized source signal; H1 = 0.97·H0; H2 = 0.94·H0: intentionally simple synthetic spatial interpolation for UI demonstration, **not independent physical measurements** or a magnetic-field simulation.
- Displays actual per-rail source witnesses, interlock status, and a per-command checksum; exports JSON receipts.

## Explicit command-driven clamp state machine

`IDLE → APPROACH → ALIGN → ATTACH → VERIFY (two different ticks) → SECURED → RELEASE → COMPLETE`

Interlocks: required sensors present, outer carrier alignment, counterspinning sun/ring score ≥0.98, delay-line response ready and matched, ground active, synthetic clamp alignment. A violated guard moves an active clamp sequence to `SAFE_HOLD`. In a hold, **the `clampAttached` flag is preserved**; reset is blocked until explicit `RELEASE` and completion of retract. Repairs never automatically unlock a latched hold; no automatic transitions are made from sampled sensor values except monitoring the safety interlocks.

The receipt sequence is deterministic, with 32-bit FNV-1a witness/command checksums and a last-96-entry history. **These are not cryptographic signatures**, persistent tamperproof records, or proof of a real transporter. Receipt sequence numbers continue even after older entries rotate out of the display buffer.

## Tests

```
node tests/test_models.cjs
python tests/browser.py
```

Checked locally: 117,630 pure-model assertions covering rail counts/readings, 19 identities, baseline comparison, clamp progression, fresh-tick verification, rail open, misalignment, false release rejection, unsafe reset refusal, forced retract, witness checksums, ledger closure, receipt bounds. Chromium browser automation also checks desktop and mobile, sequence progression, safe holds, repair/reset, export to JSON/TXT/PNG, and ASCII.

## Scientific boundary

The HARVESTER is a user-defined symbolic transport/control architecture, not a working hardware harvester, electromagnet, gyroscope-propelled transporter, or source of gravity. Real Hall sensors would need biasing, calibration, measured magnetic fields in physical units, material/temperature effects, control-loop stability, torque budgets, dimensions and mechanical validation. Those do not exist in this prototype.

## Source

GitHub: `DavidWise01/oasis/apps/game-gear-zero/labs/harvester-hall-clamp-v10/`

Predecessor v8: `apps/game-gear-zero/labs/five-pulsar-torque-exchange-v8/` remains intact.
