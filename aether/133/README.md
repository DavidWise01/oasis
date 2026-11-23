# AETHER-133 — Failed packet fixture (preserved)

This initial local test is **FAILED**, not accepted. The simulator recorded 400 paired episodes, 9,600 decisions/policy and **5,600 tests**, but **240 signature-integrity episode checks failed**, particularly during path substitution, counter rollback and expired certificate fixtures.

**Cause:** The packet mutation helper passed the existing `mac` field back into its HMAC-signing operation, making its own altered packet fail verification. This falsely reduced signed-only comparator unsafe ACT to **2,000**, rather than the properly signed attack total of 3,200. Guarded unsafe ACT stayed 0, but the validity gate failed.

The predeclared gate was not met. No phase progress is awarded here. See [AETHER-133B](../133b/) for the corrected signing fixture, **5,600/5,600 passing checks** and accepted 62.5% synthetic phase status.

All results and traces are retained unchanged.
