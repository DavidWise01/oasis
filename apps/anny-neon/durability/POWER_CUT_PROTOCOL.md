# ANNY Power-Cut Boundary — Sacrificial Hardware / Independent Witness

**Status: NOT RUN / NOT CERTIFIED.** This repository contains a preparation, witness and post-reboot **candidate-evidence** protocol. It has **no electrical power control** and never issues shutdown/reboot commands.

The earlier SQLite subprocess-SIGKILL report and Chromium test plans are separate evidence classes. Neither establishes loss of mains power. SQLite's `WAL` / `synchronous=FULL` requests a sync at transaction commit, but whether a power-cut survives depends on the actual operating system, controller and storage hardware. See [SQLite PRAGMA synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous), [SQLite atomic commit assumptions](https://sqlite.org/atomiccommit.html), and [SQLite corruption safeguards](https://www.sqlite.org/howtocorrupt.html).

## Equipment and constraints

The **target** is a non-production sacrificial Linux device with replaceable storage, no sensitive information, and an operator authorized to interrupt its power. A **witness** is a separate, continuously powered physical computer (ideally on its own power feed) with durable storage. An independent switched-PDU or measured voltage trace is recommended; witness keyboard input is only an operator statement, not independent power measurement. **Never** interrupt the user's laptop, primary disk, storage server, or a live production endpoint.

The Python gate writes only synthetic bytes `01 02 03 04 05` into new SQLite DBs under a deliberately marked scratch directory. It cannot power off the target. A test that simply kills a process is **not** a power-cut run.

## Stage A — Prepare target (sacrificial machine)

On the target, with the scratch device already mounted at the example path:

```bash
mkdir -p /mnt/sacrificial/anny-test
printf 'ANNY_SACRIFICIAL_STORAGE_ONLY\n' > /mnt/sacrificial/anny-test/ANNY_SACRIFICIAL_STORAGE_ONLY
python3 apps/anny-neon/durability/powercut_gate.py prepare \
  --root /mnt/sacrificial/anny-test \
  --case RECEIVER_UNCOMMITTED --ack-sacrificial
```

The output includes a unique `run-...` directory and manifest. The script refuses roots without the exact safety marker, symlinked markers, `/`, and the user's home directory. This is an acknowledgement gate, **not** independent proof that the drive is disposable. Ensure the operator has verified the hardware.

One independent run is required for each case:
- `PREPARE_UNCOMMITTED`: expected journal ABSENT, effect 0, Violet HELD.
- `COMMIT_UNCOMMITTED`: PREPARED, effect 0, HELD.
- `RECEIVER_UNCOMMITTED`: RELEASE_PENDING, effect 0, HELD.
- `CONFIRM_UNCOMMITTED`: RELEASE_PENDING, effect 1, HELD.
- `CONFIRM_COMMITTED`: CONFIRMED, effect 1, VERIFIED.

## Stage B — Independent witness (separate machine)

Copy the target manifest to an **independent** witness computer by an appropriate transfer mechanism. Retain an unedited copy and never store the sole witness log on the target disk.

```bash
python3 powercut_gate.py witness --manifest ./copied-manifest.json \
  --ledger ./witness.jsonl --event REGISTER --operator-note 'Manifest received'
```

The witness records its host identity, observed UTC timestamp, run ID, manifest digest, and a SHA-256 linked entry. The script rejects the same hostname/machine ID and a wrong event order. A hash chain detects unsanctioned changes absent complete rehashing; **it is not a digital signature** and cannot prove a human-reported observation is true.

## Stage C — Arm and physically observe (target and witness)

On the sacrificial target:

```bash
python3 apps/anny-neon/durability/powercut_gate.py arm \
  --manifest /mnt/sacrificial/anny-test/run-<ID>/manifest.json \
  --seconds 600 --ack-sacrificial
```

A status line `ARMED_EXTERNAL_POWER_ACTION_ONLY` means the selected WAL transaction is open (or, for `CONFIRM_COMMITTED`, already committed). The script never triggers electrical power control. If no cut happens before the hold expires, uncommitted writes are rolled back and the attempt must **not** be treated as a power interruption. No automated interruption timing or device-specific electrical instructions are provided.

Only a qualified, authorized operator should interrupt the sacrificial target's power using an appropriate external device. The independently powered witness logs the observation:

```bash
python3 powercut_gate.py witness --manifest ./copied-manifest.json \
  --ledger ./witness.jsonl --event OFF_OBSERVED --operator-note 'Target power independently observed off'
python3 powercut_gate.py witness --manifest ./copied-manifest.json \
  --ledger ./witness.jsonl --event ON_OBSERVED --operator-note 'Power returned; target rebooted'
```

The witness log is a manually recorded claim. To elevate evidence beyond operator notes, collect an independent PDU/meter trace with device ID, cut timestamps, and reviewable provenance.

## Stage D — Read-only post-boot audit (target)

After reboot, copy the witness JSONL log back from the external witness; do not copy the whole disk image over the test media.

```bash
python3 apps/anny-neon/durability/powercut_gate.py verify \
  --manifest /mnt/sacrificial/anny-test/run-<ID>/manifest.json \
  --ledger ./copied-witness.jsonl --report ./target-recovery-evidence.json
```

`verify` separately opens journal and receiver files, checks WAL recovery and `PRAGMA integrity_check`, compares expected state and `effectCount`, verifies source digest and unchanged transfer identity, checks a **new Linux boot ID**, and checks witness log order / chain / separate-host identity.

**The maximum programmatic status is `EVIDENCE_CANDIDATE_MANUAL_REVIEW`; the report always has `"certified": false`.** Manual, independent power and hardware evidence is needed before any claim of actual electrical-interruption survival. If requirements are absent or any state mismatches, the result is `NOT_CERTIFIED`. Never copy a candidate back into the readiness registry as a certified result without a review process.

## Self-test (does not cut power)

On any suitable Python 3 Linux runner:

```bash
cd apps/anny-neon/durability
python3 powercut_gate.py self-test
python3 -m unittest -v test_powercut_gate.py
```

These tests use temporary synthetic scratch fixtures and mock a separate witness **only** in the unit tests. They are negative controls: regardless of local test success, no physical power interruption is certified.

## Boundary exclusions

- No production hardware, real user transfers, or hidden power-switch actions.
- No proof of storage controller truthfulness, write-cache/barrier compliance, sector failure behavior, or filesystem/kernel recovery on every device.
- No proof of distributed exactly-once external I/O, quantum/physical force coupling, or electrical-waveform authenticity from a hand-entered witness log.
- No modification to ANNY's 18-position cubit, 10 ACKs, immutable protocol stages, Sapphon colors or Greek `− / +` names, `-- VOID` or `++ GRAVITY`.

**Next certification boundary** (only after actual authorized hardware access): review a witnessed electrical meter/PDU log paired with all five post-boot recovery reports, then scope the pass to that exact drive, filesystem, firmware, power hardware, and test sequence.
