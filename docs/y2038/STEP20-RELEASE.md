# Step 20 — fail-closed production release gate

**Outcome: BLOCKED / NOT PRODUCTION READY.**

Run `python3 docs/y2038/check_step20.py` to test the release-gate rules (8/8 local synthetic checks). Run `python3 docs/y2038/step20_release.py` to assess actual release evidence: with no injected key or approved external evidence, expected exit code is **1**, with `decision: BLOCKED`. Zero exit code is reserved for complete authenticated current attestations and their digest-matching evidence files.

Required independently reviewed evidence names: `consensus_multi_leader_safety`, `durable_wal_restart`, `quorum_partition_recovery`, `mtls_membership_replay`, `snapshot_restore_backup_drill`, `multi_host_chaos_test`, `formal_protocol_verification`, `operations_runbook_and_monitoring`.

The optional `Y2038_RELEASE_ATTESTATION_KEY` must come from a protected external secret manager, never from this repository. Even a green gate does not make the attestations true: reviewers must independently verify underlying evidence and avoid self-attestation. HMAC is a simple illustrative provenance check, not a managed multi-reviewer signature chain.

**Safety rule:** Synthetic fixtures are for unit tests ONLY. They do not count as production evidence. The old Step 11–19 models and their CI passes do not prove full Raft consensus, independently durable multi-host replication, true mTLS, authenticated dynamic membership, power-cut safety or deployment readiness.

Milestone files 20/20 do not imply operational certification. Next work is to replace bounded models with a reviewed consensus system and generate external evidence; stay BLOCKED until then.
