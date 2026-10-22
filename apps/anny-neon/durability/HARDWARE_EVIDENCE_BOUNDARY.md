# ANNY Hardware Identity + Signed Recovery Boundary (v1)

**Status: SYNTHETIC GATE PASSED · PHYSICAL POWER CUT NOT RUN · NOT CERTIFIED**

This is the next evidence boundary after the two-source Ed25519 witness/meter gate. It combines:
1. An independently pinned SHA-256 **policy** specifying three distinct Ed25519 public keys: witness, meter, target recovery.
2. Signed **meter readings** with exact power circuit, meter channel, meter serial, calibration-file SHA-256, and measurement kind `rms_voltage`.
3. A separately signed **post-boot target recovery snapshot** bound to the original run, its manifest, the target machine/disk/firmware/filesystem identities, the changed boot ID, and the expected receiver/journal state.
4. Time ordering: post-boot recovery signature must be timestamped after the signed restored-voltage observation and within the policy's one-day audit window.

**It never toggles electrical power, signs real events, provisions private keys, or issues an automatic certificate.** Success means `AUTHENTICATED_HARDWARE_EVIDENCE_CANDIDATE`, with `certified: false` and `physical_power_loss_certified: false`. A valid signature proves possession of a private key, not that the associated meter, disk or person was truthful.

## Versioned implementation

- `durability/hardware_boundary.py` — offline Python verifier
- `durability/test_hardware_boundary.py` — 21 disposable-key tests including wrong circuit, cloned signer, changed disk, duplicate ledger effects, forged target signature, unchanged boot, and recovery before power restoration
- `durability/witness_attestation.py` — prior two-source Ed25519 verification, unchanged
- `durability/hardware-synthetic-test-evidence.json` — executed 37/37 local tests (16 previous + 21 new)

## Trusted inputs required for a *real* candidate

A **policy hash received out of band**, not computed from the supplied policy during verification. The policy must include an additional `target` object with `device_id` and `ed25519_public_key_b64` and a `hardware` object with **exactly** these fields:

```json
{
  "machine_id": "INDEPENDENTLY-RECORDED-MACHINE-ID",
  "disk_serial": "INDEPENDENTLY-RECORDED-DISK-SERIAL",
  "disk_model": "MODEL-IDENTITY",
  "disk_firmware": "FIRMWARE-IDENTITY",
  "filesystem_uuid": "SACRIFICIAL-FS-UUID",
  "power_circuit_id": "EXTERNAL-POWER-BRANCH-ID",
  "meter_channel_id": "INDEPENDENT-METER-CHANNEL",
  "meter_serial": "INDEPENDENT-METER-SERIAL",
  "meter_calibration_sha256": "64-lowercase-hex-digits"
}
```

The witness and meter policy entries remain as in the previous `anny-witness-trust-policy-v1` scheme. The three public keys and device IDs must all differ. The meter must include `power_circuit_id`, `meter_channel_id`, `meter_serial`, `meter_calibration_sha256`, and `measurement_kind: rms_voltage` in **each signed payload**. Meter values must satisfy the existing pinned off/on thresholds and time correlation policy.

The target's recovery evidence is a single Ed25519-signed envelope:

```json
{
  "payload": {
    "schema": "anny-signed-target-recovery-v1",
    "run_id": "THE-SACRIFICIAL-RUN",
    "manifest_sha256": "HASH-OF-PRE-CUT-MANIFEST",
    "device_id": "INDEPENDENTLY-PINNED-TARGET-SIGNER",
    "machine_id": "TARGET-MACHINE-ID",
    "hardware": {"...": "exact match to pinned hardware policy"},
    "preboot_boot_id": "BOOT-ID-BEFORE-CUT",
    "postboot_boot_id": "BOOT-ID-AFTER-RESTORATION",
    "snapshot": {
      "state": "CONFIRMED",
      "receipt": true,
      "effect_count": 1,
      "receiver_rows": 1,
      "violet": "VERIFIED",
      "integrity": ["ok", "ok"],
      "source_consistent": true
    },
    "observed_utc": "ACTUAL-POST-RESTORE-UTC-TIMESTAMP"
  },
  "signature_b64": "BASE64-ED25519-SIGNATURE-OVER-CANONICAL-PAYLOAD"
}
```

The snapshot above is an illustrative `CONFIRM_COMMITTED` fixture; the verifier derives the actual expected values for each of the five interruption cases. **No real device values or credentials are supplied in this repository.**

## Offline verification (does not touch a target disk)

```bash
cd apps/anny-neon/durability
python -m pip install 'cryptography==46.0.4'
python hardware_boundary.py \
  --manifest /copy/manifest.json --policy /separate/pinned-policy.json \
  --trusted-policy-sha256 HASH_FROM_DIFFERENT_TRUST_CHANNEL \
  --witness /copy/witness.jsonl --meter /copy/meter.jsonl \
  --recovery /copy/target-signed-recovery.json \
  --report /audit/candidate.json
```

No actual power control or signing key generation occurs in the verifier. The verifier checks signatures, identity matching, bounds, recovery state and timing. It cannot independently attest the physical serial number, meter calibration, drive cache, power waveform, or actual disk contents; those require authenticated instruments, trusted inventory and separate review.

## Reproduced local unit evidence

2026-10-22T04:29:02Z, Python 3.13.5 / cryptography 46.0.4 on Linux:
`python -m unittest -v test_witness_attestation.py test_hardware_boundary.py`

- **37 tests executed, 37 passed**, zero failures
- Local source SHA-256 and all test case names are pinned in `hardware-synthetic-test-evidence.json`
- Test-only ephemeral signing keys never enter GitHub
- The GitHub files for the two *new* Python modules match the locally executed files by Git blob hash

**Physical scenarios 0/5, real independent meter and target 0 connected.** Retain `NOT_CERTIFIED` in `powercut/readiness.json`. Runner completion is a separate CI issue; no GitHub-hosted result is asserted here.

## Natural next physical boundary

Connect an **externally owned and independently pinned** meter and sacrificial storage device, collect a signed trace through a qualified, authorized physical interruption, and compare its immutable evidence to independently collected post-reboot disk measurements. Until that is done, this is a proof of software evidence checking only.
