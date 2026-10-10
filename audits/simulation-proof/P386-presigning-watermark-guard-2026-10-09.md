# P3.86 pre-signing watermark guard

Date 2026-10-09. Local Node v22.16.0 test **PASS_WITH_EXTERNAL_TRUST_ASSUMPTION**, 14 assertions, 64 concurrent same-epoch attempts (1 accepted, 63 blocked), 1485.68ms end-to-end test run. Actual child process was terminated by SIGKILL; its orphaned lock prevented subsequent signing (fail closed). Tests also covered restart, replay, deletion of latest local witness, wiped local history, missing/unavailable external watermark.

The prototype ensures local witness latest signed record equals independently retained watermark **before signing**. It uses an exclusive mkdir lock. **RetainedWatermark is an in-memory NONDURABLE mock**; if its state is rolled back, the guarantee fails. Signing and publication into external trust are not atomic, and interrupted external publication requires deliberate recovery; no production guarantee. Root topology -+5 + 1 and seven OSI / 100 symbolic projection layers unchanged.

Code and runnable dependency bundle are provided as P3.86 conversation artifacts; source files have not been committed here. Next P3.87 should implement authenticated orphan-lock recovery and externally durable atomic checkpoint publication.
