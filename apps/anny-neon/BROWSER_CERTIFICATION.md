# ANNY Browser Certification Boundary

This checkpoint turns the previous JavaScript-only geometry checks into a reproducible **real Chromium** gate, using the exact GitHub Pages source tree served over local HTTP.

## Run in GitHub Actions

Workflow: `.github/workflows/anny-chromium-boundary.yml`

Trigger: pushes on `main` touching `apps/anny-neon/**`, or manual `workflow_dispatch` in the GitHub Actions UI. Requires GitHub Actions enabled for the repository.

The workflow:
1. Runs three deterministic Node test files (`sapphon-spectrum`, `radiation-overlay`, and `sapphon-geometry`).
2. Installs Python Playwright and Chromium.
3. Serves the repository root over an ephemeral `127.0.0.1` HTTP port (secure-context browser APIs are available on localhost).
4. Runs `apps/anny-neon/tests/browser_gate.py`.
5. Uploads `anny-chromium-browser-evidence` (JSON report and screenshot) even if a gate fails.

## Reproduce on workstation

```bash
python -m pip install playwright==1.57.0
python -m playwright install chromium
python apps/anny-neon/tests/browser_gate.py
```

Set `ANNY_CHROMIUM_EXECUTABLE=/usr/bin/chromium` to use an existing Chromium binary. Output defaults to `anny-browser-evidence/` at the checkout root. Do not commit browser profiles or sensitive browser data.

## Browser checks

- Page JavaScript initializes, seven Greek signed pairs and four radiation toggles mount.
- Two active photon markers, two active particle markers, and independent toggle behavior.
- Gamma/X-ray hiding does not suppress beta. Restore-all resumes both tracks.
- Green and Anny/Violet focus display the expected Greek names and wavelength endpoints.
- `-- VOID`, `++ GRAVITY`, and White broadband remain independent.
- Completing a 40-bit transfer produces `CONFIRMED / VERIFIED` with one ledger effect.
- Same-session three-check recovery gate passes.
- Chromium context closes entirely and **relaunches as a new browser process with the same on-disk browser profile**.
- Transfer ID and independent IndexedDB evidence survive restart. Reload retains the exact transfer ID.
- Five duplicate deliveries still report one ledger-managed effect after restart.
- Presentation-only radiation toggle selection resets on page reload, unlike transfer evidence.

## Certification boundary

Passing this gate verifies browser process restart after a **graceful close**, not forced termination during a transaction, storage fsync after OS crash, abrupt power loss, distributed exactly-once external side effects, or cross-device federation. The browser runs against a localhost origin, not the remote deployed Pages domain. Additional online deployment tests remain a separate gate.

No geometrical visualization has the authority to ACK, commit, release, or rewrite the journal.
