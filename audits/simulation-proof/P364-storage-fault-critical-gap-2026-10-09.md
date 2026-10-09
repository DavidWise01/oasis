# P3.64 — Storage-fault test: lost reservation vulnerability

Date: 2026-10-09. Tested local Node.js v22.16.0 against the P3.61 CrashWitness implementation. Six simulated storage-fault scenarios; 12 assertions pass **because the test explicitly expects and demonstrates one vulnerability**. Truncated JSON, empty JSON, corrupted stored digest, damaged stored signature and stale pending file reject a conflicting same-epoch request. Removing the entire reservation file permits a fresh, conflicting same-epoch signature to be generated.

Status: **KNOWN CRITICAL SAFETY GAP, NOT FIXED.** Do not interpret PASS_WITH_CRITICAL_GAP as a security pass. An attacker or storage failure that removes the sole per-epoch reservation can reopen an already signed epoch. Further loss/corruption modes also need testing.

Remediation: enforce a durable, independently authenticated, non-rollbackable witness signing watermark or an authoritative transactional database retaining epoch reservations. Fail closed if external trusted state cannot be verified, including when the local reservation is missing; avoid approving a new vote simply because no local file is found. Then stress-test that fix across abrupt shutdowns and recovery. These are symbolic consensus witnesses, not photon physics.
