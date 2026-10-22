# ANNY — Signed Independent Witness / Meter Evidence Boundary

**Date:** 2026-10-21 (experiment executed at 2026-10-22 03:37 UTC).  
**Verifier:** `apps/anny-neon/durability/witness_attestation.py`  
**Tests:** `apps/anny-neon/durability/test_witness_attestation.py`  
**Recorded outcome:** `apps/anny-neon/durability/signed-evidence-local-run.json`  

## Design

The earlier SHA-256 linked manual witness log is **not authenticated**: a person with complete control of its bytes could re-hash the full chain. This new additional *offline* gate authenticates two separately signed streams using Ed25519 and checks them against a previously trusted public-key policy.

The evidence streams are distinct:

- **Witness:** REGISTER → OFF_OBSERVED → ON_OBSERVED, each with role, device, run, manifest digest, sequence, nonce and aware UTC time.
- **Meter:** BASELINE_VOLTAGE → ZERO_VOLTAGE → RESTORED_VOLTAGE, including an independently signed measured voltage for each event.

The verifier requires *two different public keys and device identifiers* and an **out-of-band SHA-256 trust-policy hash** provided directly to the verifier. It also checks each event signature, run identity, sequence, nonce uniqueness, manifest binding, meter on/off thresholds and cross-stream clock skew.

**Critical distinction:** Ed25519 verifies that the holder of the expected key signed the claims; it does not prove the physical meter was attached to the target supply, independently calibrated, or uncompromised. Even six valid signatures with plausible voltages produce only `AUTHENTICATED_EVIDENCE_CANDIDATE`, with `certified: false` and `independent_electrical_measurement_confirmed: false`. Only an independent real-world hardware and post-reboot review can support a scoped electrical-test claim. No private keys are stored in the repository.

## Verify offline

Use approved hardware to export the original manifest, witness JSONL, meter JSONL and separately pinned verifier policy. The policy must contain:

```json
{
  "schema": "anny-witness-trust-policy-v1",
  "manifest_sha256": "<real manifest digest>",
  "witness": {
    "device_id": "<independently identified witness>",
    "ed25519_public_key_b64": "<independently pinned 32-byte public key>"
  },
  "meter": {
    "device_id": "<independently identified voltage meter>",
    "ed25519_public_key_b64": "<different, separately pinned public key>"
  },
  "voltage_thresholds": {"off_max_v": 5, "on_min_v": 100},
  "max_witness_meter_skew_seconds": 10
}
```

**The voltage thresholds are illustrative, not universal.** A qualified test operator must derive limits for the actual supply and instrument, and independently pin the policy's digest before receiving event files. The trust digest must not be copied uncritically from the same untrusted evidence bundle.

```bash
python -m pip install 'cryptography==46.0.4'
python apps/anny-neon/durability/witness_attestation.py verify \
  --manifest manifest.json --policy signed-policy.json \
  --trusted-policy-sha256 <independently-pinned-policy-SHA256> \
  --witness signed-witness.jsonl --meter signed-meter.jsonl \
  --report signed-audit-result.json
```

The tool performs **verification only**; it never creates keys, signs fictitious meter readings, powers off a machine, or changes the frozen Harvester receiver/journal.

## Executed proof-of-software

The test suite uses ephemeral, unrelated Ed25519 private keys and **synthetic readings** of 120 → 0 → 120 V. An offline Python execution with `cryptography==46.0.4` passed **16/16 tests**. Tested source Git blob SHA: `e7f7e55b407fd1950f27f3e7865930239ee7e1ea`; test Git blob SHA: `eb7854a342bb637c9fac897d8fa204583b91504c`. Those exact blobs were independently re-fetched from GitHub after the commit.

The suite checks the valid candidate, changed signed payload, repeated meter event, replayed nonce, wrong signer, reused signing key, altered trust policy, wrong run ID, absent voltage dip, missing event, reversed time, mismatched clocks, invalid voltage type, altered manifest, missing trusted policy hash, and event reorder.

### Remaining certification boundary

The earlier **27 Python manual-witness tests** are committed and configured for GitHub Actions, but a successful remote result has not been verified in this conversation. Physical power-loss experiments remain **0/5 NOT_RUN**, and signed meter data from any actual independent instrument has **not** been collected.

To approach hardware certification: independently pin both public keys and the policy, validate meter calibration and placement, externally observe a real sacrificial-target interruption, run a post-reboot filesystem+database inspection, and reconcile timestamps and identities with the unsigned and signed records. The output must then be reviewed and scoped to that hardware. Automated statuses cannot bypass this review.
