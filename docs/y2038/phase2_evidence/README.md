# Phase 2.5 — auditable cluster-test evidence collector

Run from `docs/y2038/phase2_cluster`:

```sh
python3 ../phase2_evidence/evidence.py --output ./private-evidence/run-01 -- python3 run_cluster_test.py
```

Outputs `report.json` and `run.log` with exit status, UTC start/end times and SHA-256 of logs. The collector exits nonzero if the command fails, times out, or cannot be launched. Local unit tests: **7/7 passed** in the authoring container. It does not silently mark an absent Docker cluster as successful.

**Scope:** A SHA-256 hash alone is not an authentic signature; command output can be forged by an untrusted test; local clock is not a trusted time source; logs may include secrets. Keep reports in controlled storage with access restrictions, review and redact logs, and independently attest external evidence. Do not put private run logs or TLS keys into public GitHub.

Not tied into Step 20's signed release records on purpose: release_attestation is always false. Independently verified cluster results plus approved review are still necessary before the release gate can open.

Production status: BLOCKED.
