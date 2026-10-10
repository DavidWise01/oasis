# P3.90 — `{-{+{%}+}-` blockade around fencing epochs

Local Node.js v22 regression: 26/26 assertions passed. The proposed symbolic blockade wraps a SQLite fencing authority with a retained epoch/token witness verification gate. The test rejected a coherent historical SQLite snapshot when the witness retained the newer epoch, stale fencing tokens, unavailable external witness, and a split-brain publication failure after local fencing commit. A valid lease succeeded, and ordinary restart preserved continuity when witness state was retained.

**Open:** The provided witness is only an in-memory test double, not an independently durable trusted service. The local acquire/remote publish sequence is not atomic: a publication outage causes quarantine and requires authenticated reconciliation. Two writers may race through local acquire and witness publication; this test did not establish a complete distributed multiwriter protocol. Coordinated rollback of both stores defeats this model. No physical solar-photon claims or evidence of quantum decoherence arises from the simulation. The seven OSI / 100 symbolic layer overlay and -+5 + 1 outer topology remain design constraints.

Executable P3.90 kernel, test, result JSON, P3.89 dependency and README are in the user-facing ZIP artifact.
