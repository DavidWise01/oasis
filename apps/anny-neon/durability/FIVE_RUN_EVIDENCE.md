# ANNY Five-Run Signed Evidence Ingestion — Boundary v1

**Status: SYNTHETIC TESTS PASS · 0/5 PHYSICAL POWER CUTS RUN · NOT CERTIFIED.**

This is an offline, read-only verifier for **five separately captured and independently signed** hardware power-interruption candidates, not an apparatus for creating those measurements. It never toggles electrical power, generates private keys, changes disk contents, or asserts that a physical event actually occurred.

## Components

- `five_run_gate.py` — five-run correlation and provenance check, built atop `hardware_boundary.py` and `witness_attestation.py`.
- `test_five_run_gate.py` — 16 synthetic positive/negative controls using temporary Ed25519 keys.
- `five-run-synthetic-validation.json` — local **53/53 PASS** from the 16 new and 37 existing signed-evidence tests, with source SHA-256 digests.
- `.github/workflows/anny-powercut-readiness.yml` — invokes the updated tests on GitHub Actions. A completed runner report still requires separate verification.
- `powercut/readiness.json` — physical scenarios are all **NOT_RUN / NOT_CERTIFIED**.

## The five independently anchored runs

Use a new directory for each event, with signed `manifest.json`, `policy.json`, `witness.jsonl`, `meter.jsonl`, and `recovery.json`. The manifest/policy contents must use the schemas already required by `hardware_boundary.py`.

A real `batch.json` MUST have this exact schema (replace the placeholders, do not commit private keys or confidential meter identifiers to public Git):

```json
{
  "schema": "anny-five-run-evidence-batch-v1",
  "runs": [
    {"case": "PREPARE_UNCOMMITTED", "manifest": "case-0/manifest.json", "policy": "case-0/policy.json", "witness": "case-0/witness.jsonl", "meter": "case-0/meter.jsonl", "recovery": "case-0/recovery.json", "trusted_policy_sha256": "REPLACE_WITH_EXTERNALLY_ANCHORED_POLICY_SHA256"},
    {"case": "COMMIT_UNCOMMITTED", "manifest": "case-1/manifest.json", "policy": "case-1/policy.json", "witness": "case-1/witness.jsonl", "meter": "case-1/meter.jsonl", "recovery": "case-1/recovery.json", "trusted_policy_sha256": "REPLACE_WITH_EXTERNALLY_ANCHORED_POLICY_SHA256"},
    {"case": "RECEIVER_UNCOMMITTED", "manifest": "case-2/manifest.json", "policy": "case-2/policy.json", "witness": "case-2/witness.jsonl", "meter": "case-2/meter.jsonl", "recovery": "case-2/recovery.json", "trusted_policy_sha256": "REPLACE_WITH_EXTERNALLY_ANCHORED_POLICY_SHA256"},
    {"case": "CONFIRM_UNCOMMITTED", "manifest": "case-3/manifest.json", "policy": "case-3/policy.json", "witness": "case-3/witness.jsonl", "meter": "case-3/meter.jsonl", "recovery": "case-3/recovery.json", "trusted_policy_sha256": "REPLACE_WITH_EXTERNALLY_ANCHORED_POLICY_SHA256"},
    {"case": "CONFIRM_COMMITTED", "manifest": "case-4/manifest.json", "policy": "case-4/policy.json", "witness": "case-4/witness.jsonl", "meter": "case-4/meter.jsonl", "recovery": "case-4/recovery.json", "trusted_policy_sha256": "REPLACE_WITH_EXTERNALLY_ANCHORED_POLICY_SHA256"}
  ]
}
```

Store `batch.json` in the same evidence root with the five case subdirectories. Do **not** treat an ordinary freshly computed hash as trusted: the SHA-256 batch digest must have been pinned through an independent, pre-authorized mechanism outside the test machine and the bundle itself.

```bash
cd apps/anny-neon/durability
python -m pip install 'cryptography==46.0.4'
python -m unittest -v test_witness_attestation.py test_hardware_boundary.py test_five_run_gate.py

python five_run_gate.py \
  --root /path/to/private-evidence \
  --bundle /path/to/private-evidence/batch.json \
  --trusted-bundle-sha256 <INDEPENDENTLY_RECORDED_64_HEX> \
  --report /path/to/private-output/five-run-audit.json
```

## Fail-closed boundary

Every run must authenticate its own distinct Ed25519 witness/meter/target signatures, manifest, pin, voltage observations, hardware/target identity, and postboot journal/receiver recovery snapshot. The **aggregate** then requires:

1. Exactly five distinct run IDs in the canonical phase order.
2. One identical hardware identity and the same three signing keys/device IDs across all five runs.
3. Unique witness/meter nonces and no reused evidence-file digests across the batch.
4. Exact boot continuity: each run's preboot ID equals the preceding run's postboot ID.
5. A non-overlapping signed timeline: next meter baseline is after the previous signed recovery record.
6. No absolute/parent-traversal/symlink evidence paths and no missing files.

**Important:** Boot continuity presupposes a sequential five-cut experiment on the *same sacrificial target* with no intervening reboot. If the real experiment intentionally reboots between scenarios, this strict profile rejects the evidence; it must not be weakened silently.

Even if every signature, hardware ID, and byte matches, the highest automatic status is `AUTHENTICATED_FIVE_RUN_EVIDENCE_CANDIDATE`; `certified: false` and `physical_power_loss_certified: false` remain immutable outputs. Real voltage measurement still needs a trusted device calibration/provenance process, authenticated timestamps, electrical trace interpretation, and independent human review. Signed data proves provenance under pinned keys, not physical truth.

## Confirmed local synthetic tests

The combined offline suite executed **53/53 PASS** in a Linux Python environment: 16 new five-run checks plus the prior 37 witness/hardware signature checks. These were synthetic Ed25519 keys, synthetic meter readings, and invented boot identities. No hardware has been connected, and **none of the five physical interruption cases has occurred or been certified**.

The frozen Harvester stages, ACK logic, 18 cubit witness positions, seven Sapphon pairs, radiation overlay, `-- VOID`, and `++ GRAVITY` are not touched.
