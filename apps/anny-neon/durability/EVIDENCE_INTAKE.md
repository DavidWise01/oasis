# ANNY v16.1 — Offline Five-Run Evidence Intake / Quarantine

**Engineering result: 65/65 local synthetic tests passed. Physical power cuts: 0/5. Certification: NOT CERTIFIED.**

This boundary accepts a pre-collected five-run bundle from a **private, offline directory** and combines the existing [signed witness + meter](witness_attestation.py), [hardware-bound recovery](hardware_boundary.py), and [five-run continuity](five_run_gate.py) verifiers. It does **not** power off equipment, enroll signing keys, invent measurements, upload files, or issue a certificate.

## Intake contract

- Exactly **26 files**: one `batch.json` and five files per each of five ordered runs (manifest, policy, witness, meter, recovery).
- The batch SHA-256 must come from **an independent, out-of-band source**. Computing a hash from an untrusted bundle and using it as its own anchor does not prove provenance.
- Exact filenames and paths must match `batch.json` and stay under the evidence directory.
- Extra files, hidden files, symlinks, hardlinks, duplicated paths, missing files, oversized files, and private-key PEM content fail closed.
- All 25 individual evidence files are inventoried by content SHA-256. Their Ed25519 signatures, trusted per-run policy anchors, hardware identities, boot transitions, nonce uniqueness, event order, voltage thresholds and recovery consistency are then checked by the pre-existing five-run verifier.
- The receipt omits raw serials, device IDs, signatures and Ed25519 public keys. **File hashes are still potentially identifying** and should not automatically be made public.
- Even a fully matching synthetic dataset yields `AUTHENTICATED_REVIEW_REQUIRED`, with `certified=false` and `physical_power_loss_certified=false`.
- An incomplete or unauthenticated bundle yields `QUARANTINED`; no automatic reprocessing or promotion to authority occurs.

## Offline use

Install Python and the verifier-only dependency on a trusted inspection machine:

```bash
python -m pip install 'cryptography==46.0.4'
python apps/anny-neon/durability/evidence_intake.py \
  --root /secure/private/anny-raw-five-run \
  --bundle /secure/private/anny-raw-five-run/batch.json \
  --trusted-bundle-sha256 <PREVIOUSLY_PINNED_EXTERNAL_SHA256> \
  --report /secure/private/anny-review/intake-report.json
```

Do not save `--report` inside the evidence root. Preserve raw evidence with read-only access and independent backups. Do not publish meter logs, disk serials, private keys, raw signatures, or unreviewed receipt hashes in a public Git repository.

Example output status values:

```json
{"schema":"anny-evidence-intake-v1","status":"AUTHENTICATED_REVIEW_REQUIRED","certified":false,"physical_power_loss_certified":false}
```

```json
{"schema":"anny-evidence-intake-v1","status":"QUARANTINED","certified":false,"physical_power_loss_certified":false}
```

A candidate still requires independent hardware onboarding, meter-origin verification, a witnessed electrical interruption, actual storage recovery evidence, and manual review. Neither the tool nor these tests can prove that the physical voltage readings were genuine.

## Locally executed regression evidence

The offline test command below was executed using Python 3.13.5 and `cryptography 46.0.4` on a local Linux runtime:

```bash
cd apps/anny-neon/durability
python -m unittest -q test_witness_attestation.py test_hardware_boundary.py test_five_run_gate.py test_evidence_intake.py
```

**Result: 65/65 PASS**, consisting of 53 existing synthetic signed-evidence tests plus 12 new quarantine/redaction tests. Exact source blobs matched the files committed to GitHub. The source checks and results are recorded in [intake-synthetic-validation.json](intake-synthetic-validation.json). GitHub Actions runner completion has not yet been verified.

This is **not** a physical power interruption experiment. The five physical scenarios in [powercut/readiness.json](powercut/readiness.json) remain `NOT_RUN` and the global classification remains `NOT_CERTIFIED`.

## Security boundary

This tool is an offline *review staging* gate, not a hardened parser for hostile concurrent filesystem modification. A privileged adversary modifying files during inspection can cause time-of-check/time-of-use races. For hostile sources, use an isolated inspection environment and immutable snapshots before intake. A valid Ed25519 signature authenticates a configured signing key; it cannot alone prove that a real circuit lost power or that a signer belongs to a manufacturer.

No changes were made to the frozen ANNY Harvester ACK/receiver protocol, the 18-position analytical cubit, the seven Greek signed color pairs, `-- VOID`, `++ GRAVITY`, or radiation overlays.
