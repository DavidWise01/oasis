# OASIS Gate 6 — Windows / Linux field environment

**Prepared:** October 14, 2026. **Purpose:** an operator-controlled environment to reproduce signed Astrophage OBF2 transfer, TLS 1.3 mutual authentication, an `fsync`-committed receipt, a deliberate receiver crash before ACK, restart, and a single journal record with a matching `DUPLICATE` receipt. **This package is an additive launcher, not a new KET kernel or independent security certification.**

## What is in this ZIP

| File | Use |
|---|---|
| `BOOTSTRAP.ps1` | Windows repo checkout, preflight, local test, optional provisioning |
| `gate6.mjs` | Cross-platform sender, receiver, key setup, audit and sanitized evidence generator |
| `local_smoke.mjs` | Actual local TLS 1.3 + signed OBF2 + crash/recovery test (loopback scope) |
| `test_evidence.mjs` | 12 deterministic audit-unit checks including deliberate corruption |
| `START_RECEIVER.ps1`, `SEND_EVENT.ps1` | Windows command wrappers for two endpoints |
| `INSPECT_RECEIVER.ps1`, `FINALIZE_EVIDENCE.ps1` | Produce and reconcile receipt evidence |
| `.gitignore` | Deny common secrets and runtime state if placed in a Git checkout |

The runner independently refuses key and journal state located inside the Git checkout and verifies the frozen hash before loading the relay.

**Excluded:** private keys, TLS certificates, production tokens, journal contents, live execution receipts, VM images. They must be generated locally. The actual OBF2 transport code stays in `DavidWise01/oasis` and is loaded without modification.

## Requirements

- Windows 11 x64 with PowerShell, Git, Node.js **22+** and OpenSSL available on PATH; alternatively Node 22+, Git and OpenSSL on Linux/macOS with direct `node gate6.mjs` commands.
- Network connection for the initial public `git clone`; this kit pins commit `0f1447ece052d0434edad58f57784392116d59d8` if creating a new clone.
- On separate hosts, a **private LAN or trusted VPN**, receiver reachable from sender on **TCP 32443**, firewall permitting only the sender. Do **not** expose this reference server publicly.
- A durable local disk for the receiver journal. **One writer per journal**. For the crash test, use a disposable test journal, never production data.
- To count as *two-physical-device* evidence, use two real computers. Two QEMU guests on one laptop test endpoint separation but not independent physical hardware reliability.

Useful official sites: https://nodejs.org/, https://git-scm.com/, https://www.openssl.org/ . The installer deliberately does not run elevated commands or install packages silently.

## 1. Prepare the environment (on a provisioning Windows computer)

Extract the ZIP to a private directory such as `C:\OASIS-Gate6`. Open PowerShell *in that folder* and run:

```powershell
.\BOOTSTRAP.ps1 -ProvisionKeys
```

The script checks Node, OpenSSL and Git, clones public OASIS into `./oasis`, checks out the pinned commit, verifies the frozen SHA-256, and runs the **local** authenticated crash/replay smoke test. It generates **fresh** credentials under `./gate6-state/` with `root-private/`, `server/` and `client/` folders. If keys already exist, it refuses to overwrite them. The private CA key remains on the provisioning computer; protect it and back it up offline. Client and server certificates default to 90 days.

If your shell prevents local scripts, use an execution policy appropriate to your organization, e.g. launch a single script from your PowerShell session with `powershell -NoProfile -ExecutionPolicy Bypass -File .\BOOTSTRAP.ps1 -ProvisionKeys` after inspecting it. Do not lower system-wide policy.

**For receiver B and sender A:** extract the *same ZIP* on each machine, run `./BOOTSTRAP.ps1` there **without** `-ProvisionKeys`, and transfer only the respective **`server/` folder to B** and **`client/` folder to A** by a trusted offline or encrypted channel. Place each in `<kit>/gate6-state/server/` or `<kit>/gate6-state/client/`. The code and event IDs must match on both endpoints. Do **not** copy the complete `gate6-state` tree, private CA key, or sender private key to the wrong endpoint. On Windows protect files with NTFS ACLs.

## 2. Baseline authenticated receipt (two hosts)

On **B**, start the receiver with B's private LAN address:

```powershell
.\START_RECEIVER.ps1 -BindIP '192.168.1.20'
```

On **A**, send once, then retry the same ID:

```powershell
.\SEND_EVENT.ps1 -ServerIP '192.168.1.20' -EventID 'gate6_base_001'
.\SEND_EVENT.ps1 -ServerIP '192.168.1.20' -EventID 'gate6_base_001'
```

Expected statuses: `APPLIED`, then `DUPLICATE`, with the identical 64-digit receipt. The sender writes sanitized `gate6-state/evidence/client-events.jsonl` locally. Inspect the logs; do not claim PASS merely because a process exits successfully.

## 3. Controlled crash *after* durable commit and *before* ACK

Stop B's receiver. **This is explicitly destructive to the receiver process; use only a disposable test journal.** Restart it with a crash trigger:

```powershell
.\START_RECEIVER.ps1 -BindIP '192.168.1.20' -CrashEvent 'gate6_crash_001'
```

On A:

```powershell
.\SEND_EVENT.ps1 -ServerIP '192.168.1.20' -EventID 'gate6_crash_001' -ExpectLostACK
```

The B process should exit code **86** after `fsync`, without sending ACK. A should record `LOST_ACK_EXPECTED` (a lost ACK alone does not prove a successful commit).

Restart B **without** `-CrashEvent`. On A, resend the *same* event ID:

```powershell
.\START_RECEIVER.ps1 -BindIP '192.168.1.20'   # on B, new terminal
.\SEND_EVENT.ps1 -ServerIP '192.168.1.20' -EventID 'gate6_crash_001'  # on A
```

Expected A status: `DUPLICATE` and the receipt of the single durable B record. New event IDs on A will create new journal entries; reuse the same crash ID for a true idempotent retry.

## 4. Inspect, export, reconcile evidence

On B:

```powershell
.\INSPECT_RECEIVER.ps1
```

This verifies the entire local SHA-256-linked journal without rewriting it and produces a non-secret `gate6-state/evidence/receiver-proof.json`. Verify the summary shows **exactly one entry for `gate6_crash_001`** (not one entry total; the baseline event also has one).

Copy **only this sanitized `receiver-proof.json`** to A's `gate6-state/evidence/` using your trusted transfer method. A already holds `client-events.jsonl`. Then on A:

```powershell
.\FINALIZE_EVIDENCE.ps1 -CrashEvent 'gate6_crash_001' -Mode physical
```

This generates `gate6-state/evidence/FINAL_RESULT.json`. It validates the lost ACK preceding a duplicate ACK, one durable record for that event, the matching receipt hash, matching frame hash, matching source revision, and intact journal chain. A success is labeled `PASS_IN_REPORTED_ENVIRONMENT`. Even when `-Mode physical`, the machine cannot independently prove that computers A and B have distinct hardware; add a separate human-verified host inventory and test transcript. Keep all private keys off GitHub.

For a VM-only run, select `-Mode vm`. For loopback, select `-Mode loopback`. These are **not** interchangeable with physical independence.

## 5. Run a local rehearsal before two-machine deployment

```powershell
node .\test_evidence.mjs
node .\local_smoke.mjs --repo .\oasis
```

The evidence unit tests do **not** exercise TLS. The localhost smoke test **does** create new private test credentials, run a real mTLS receiver and signed sends, crash after durable fsync, restart, inspect, and reconcile receipts. All secrets from the smoke test are deleted on completion. It prints `LOCALHOST ONLY` so this cannot be mistaken for Gate 6 physical certification.

On Linux/macOS, run the equivalent `node gate6.mjs help` and `node local_smoke.mjs --repo ./oasis` with your own key setup. The launcher uses portable module imports rather than modifying the existing release's Windows-sensitive CLI guard.

## Failure and security constraints

- **Do not expose** `32443` to the public Internet. Use LAN/VPN firewall allowlisting and a trusted provisioning route.
- Preserve key/certificate rotation dates, backup and recovery procedures, and the immutable hash of the frozen core.
- `DUPLICATE` establishes an idempotent **journal** commit under at-least-once retries, not exactly-once external actions.
- SHA-256 chaining detects journal corruption but is not tamper-proof external notarization; TLS/Ed25519 authenticate peers and sender, not scientific correctness.
- A failure may be due to DNS/IP, bad certificate, clock, missing private key, non-durable disk, or firewall. Retain diagnostic logs without exposing secrets.
- **If a run fails**, do not overwrite an existing receipt or mark production PASS. Restore the previous deployment and investigate separately.

## Source preservation

Authoritative frozen state remains under `architecture/diatom-diamond/frozen/dual5-floor-v0.7`. Pinned expected SHA-256: `47d4c89ac8155b9470852e0e23d2c059ad087eedc2b7949632a9431b5792fd4b`.

The established GitHub guide also exists at: https://github.com/DavidWise01/oasis/blob/main/architecture/diatom-diamond/final-six/TWO_DEVICE_SETUP.md . The repository's single-laptop QEMU plan is at `architecture/diatom-diamond/two-vm-laptop/README.md`; it is not an actual observed two-VM PASS by itself.

**Ready means scripts, dependencies, source integrity, and local smoke acceptance are in place. It does not mean Gate 6 has been independently run on your actual computers by ChatGPT.**