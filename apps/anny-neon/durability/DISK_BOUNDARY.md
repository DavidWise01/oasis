# ANNY v16.1 — Disk Process-Crash Consistency Boundary

**Scope:** standalone SQLite protocol analogue; separate from browser IndexedDB.  
**Date:** 2026-10-21.  
**Source:** `apps/anny-neon/durability/disk_gate.py`  
**Committed local report:** `apps/anny-neon/durability/local-process-evidence.json`  
**Pages evidence viewer:** `https://davidwise01.github.io/oasis/apps/anny-neon/durability/`  
**Automated workflow:** `.github/workflows/anny-disk-crash.yml`

## Executed evidence

A Linux container ran the Python 3.13.5 built-in SQLite 3.46.1 test with
`journal_mode=WAL` and `synchronous=FULL` in two **separate** SQLite files
(journal and receiver). The process running an uncommitted or committed
transaction was terminated via `SIGKILL`; the parent then reopened both DB
files independently.

Executed command:

```bash
python disk_gate.py --output local-evidence.json
```

The local script was rerun with the same outcome. The original local Python source
SHA-256 was:

```
b4fefec6516961d54e35b8fdf678ee0f0e32719cf401214367a1032dd13c6e47
```

The committed report reproduces the observed case states and outcomes in JSON
form. Its PASS status is evidence for the **local process-kill experiment only**,
not a claim about a remote GitHub runner.

| Case | State after worker SIGKILL | Receiver effects | Violet | Outcome |
|---|---|---:|---|---|
| PREPARE_UNCOMMITTED | ABSENT | 0 | HELD | PASS |
| COMMIT_UNCOMMITTED | PREPARED | 0 | HELD | PASS |
| RECEIVER_UNCOMMITTED | RELEASE_PENDING | 0 | HELD | PASS |
| CONFIRM_UNCOMMITTED | RELEASE_PENDING | 1 | HELD | PASS |
| CONFIRM_COMMITTED | CONFIRMED | 1 | VERIFIED | PASS |

**Local result: 5/5 PASS.** All five database integrity checks returned `ok`
for both journal and receiver files. A duplicate-effect guard was checked in
each scenario (at most one receiver row); concurrent external deliveries are
not part of this benchmark.

## What this does and does not prove

**Observed:** SQLite transaction atomicity and visibility across process
termination; committed state survives worker SIGKILL in this filesystem/runtime.
The observer determines VERIFIED only from a matching persisted journal
confirmation and independently stored receiver receipt.

**Not observed:** loss of electrical power, power-loss flush barriers, kernel
panic, controller volatile write caches, NAND flash failure, browser IndexedDB
storage, arbitrary distributed external side effects, or cross-host recovery.
SQLite WAL FULL is a configuration, not a certificate for storage-hardware honesty.
No production endpoint was contacted.

This is not interchangeable with the previously committed Chromium
`midflight_gate.py`, whose full real-browser execution remains unverified.

## Reproduce independently

Requires Python 3.10+ on Linux/macOS or another Unix-like OS supporting
`os.killpg` and `SIGKILL`. No external dependencies.

```bash
python apps/anny-neon/durability/disk_gate.py --output /tmp/anny-disk-evidence.json
```

CI also runs the same script on `ubuntu-latest` and uploads its **own** JSON
artifact. That runner result must be inspected before asserting a successful
GitHub Actions execution.

## Next physical boundary

A defensible **power-loss** experiment needs an isolated machine, sacrificial
storage, an external controlled power switch and independent observer, durable
pre-/post-event identifiers, filesystem and drive write-cache inspection,
checksums, and a witnessed re-boot. Do not test sudden electrical interruption
on a user's primary computer, filesystem, or irreplaceable data.

The original ANNY v16.1 journal/receiver modules, 10 dual ACKs, 18-slot
analytical cubit, signed Sapphon wavelength registry, VOID, GRAVITY, and
radiation overlays were not modified.
