# AETHER-145B — Corrected instrument qualification protocol readiness

**Local synthetic PASS**: 240 paired episodes, 4,800 decisions/policy, **3,840/3,840** tests passed. Signed-only 1,440 unsafe ACT; AETHER-145 failed gate 240 unsafe; 145B corrected 0 unsafe. All 3,360 safe dry-run ACT preserved, including 600 clean and 600 valid replacement actions.

Correction: independently signed bench acquisition with own reported value, uncertainty, device generation, tick and nonce must agree with the reference and DUT measurement. A forged reference that merely agrees with the untrusted DUT is rejected. Original 145 failure retained separately.

**Physical progress 0%.** Both keys are HMAC software mocks and the bench reads scenario truth directly. No real device, independent calibrated standard, same-path hardware acquisition, traceable certificate, measured uncertainty or drift/alarm test exists. The operational gate remains HOLD.

Local accepted Python SHA-256 `21be6c64d495f9dead48c584ba6e719eb12ec5292954cf00e148a72b0593288a`; the published GitHub Python is a distinct standalone demo and checkout replay is unverified. Complete local source, checks, traces, and failed version are in the downloadable ZIP in chat.

[Results](results.csv) · [Manifest](manifest.json) · [Interactive lab](index.html) · [Tracker](../PHASE-IX-STATUS.md).
