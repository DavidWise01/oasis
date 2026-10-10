# ROOT0 P4.11 — single-use genesis ledger benchmark

Date: 2026-10-10. Node 22.16.0 local regression **12/12 assertions passed**, 24 independent competing processes, exactly 1 initialization accepted and 23 refused by exclusive ledger grant reservation. Final rerun approximately 260 ms end-to-end including process startup. Grant reuse and cross-database replay rejected while ledger retained; missing ledger and mismatched deployment fail closed. An exclusive-create grant marker is durably written before local genesis initialization; a failed local initialization therefore leaves the grant consumed and quarantined.

**Critical reproduced vulnerability:** a separately re-provisioned empty ledger accepts an earlier consumed signed grant against a fresh database. The ledger is an ordinary local directory, not an independent monotonic authority. Separately signed grants can also initialize multiple databases under the same deployment name. The genesis sentinel can itself be erased or rolled back. No true power-loss test, authenticated reconciliation, external durable witness or split-site consensus. This is a security-model test, not physical decoherence validation.

Canonical notation stays `{-{+{%}+}-}` with four invisible sinks; outer `-+5 + 1`, 200-layer/200ms and 10^-36s symbolic registers are unchanged.

Runnable source, child worker, test and JSON report: user-facing P4.11 bundle. Next P4.12: one deployment ID per durable authority, signed grant linked to trusted nonrollbackable deployment registry, tests of independent genesis grants racing for the same deployment.