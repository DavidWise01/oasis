# THE PROBABILITY × AEON — Browser Arcade (GitHub Pages)

**AEON = Argon / Electron / Oxygen / Nitrogen.**

Browser-playable Gothic NES emulator with a ternary witness controller and a nested symbolic tesseract `[[[(game)]agent]engine]`. This is the public **browser port** of the ongoing Electron experimental project, not the Electron executable itself.

**Open:** https://davidwise01.github.io/oasis/apps/the-probability/aeon/


## AEON thought regression · v0.5

The arcade now includes **8 Hall response channels** and **8 bounded digital-pot wipers**. Each delivered input is compared with a before/after state and the last transition. The feedback engine:

- distinguishes \`−1\` no response, \`0\` RAM-only ambiguous, and \`+1\` visible response;
- detects true \`A → B → A\` regression and damps repeated behavior;
- modulates software input hold length and candidate preference, rather than inventing analog NES button voltage;
- persists its observations and wiper values per ROM and profile, and offers JSON export;
- accepts optional real Hall sensor samples and sends logical digipot values to an authorized serial bridge.

**To swap the new profile**, import [hall-regressive.md](./hall-regressive.md) under SWAP AGENT PROFILE.

**For physical electronics**, read [HALL-DIGIPOT-BRIDGE.md](./HALL-DIGIPOT-BRIDGE.md). A microcontroller and part-specific firmware are required; no actual Hall sensors or digital potentiometers are claimed to be connected.

The **one new cubit visual marker** is a regressive feedback ellipse whose glow follows Hall response estimates. The earlier \`−1 · 0 · +1\` points remain unchanged.

Validation: 11 isolated engine tests and an integrated synthetic-NES backend controller test (8 delivered presses, 8 witness receipts, all eight Hall channels updated). Native NES gameplay and physical circuit operation remain unverified.

## How to run

1. Open the page, preferably in Chrome or Edge.
2. Load a locally owned, legally obtained NES `.nes` cartridge. ROM data is processed locally in the browser; no ROM is included in this repository.
3. Leave **CONFLUENCE · AUTONOMOUS** selected to run the ternary diagnostic. Or select **HUMAN** for arrow keys, Z (B), X (A), Shift (Select), and Enter (Start).
4. Click **ENABLE SOUND** to unlock browser audio.
5. Observe `−1 / 0 / +1` witness receipts for all eight buttons; export the witnesses with **EXPORT WITNESSES**.

## Ternary semantics

The unresolved controller tests U, D, L, R, B, A, Select, Start, one at a time:

```
BEFORE → real PRESS → HOLD → real RELEASE → SETTLE → AFTER
```

- `−1`: no observed screen or sampled-RAM change.
- `0`: RAM-only / ambiguous difference.
- `+1`: visible screen change.

**These outcomes are not proof of gameplay success.** Select/Start probing can pause or alter a game. **SWEEP OFF** disables automatic probing.

If a button is blocked by its cooldown, the system waits rather than logging a fictitious press.

## Swap .md configurations

Use **SWAP AGENT PROFILE (.md)** in the agent panel. The browser accepts files with a fenced `aeon-config` block such as [ternary-witness.md](./ternary-witness.md). Profiles take effect without rebuilding, and the last imported configuration is remembered in local browser storage.

Supported browser settings include `tri_state_enabled`, `probe_hold_frames`, `probe_settle_frames`, `probe_retry_frames`, `decision_frames`, `state_key_mode` and `strategy`.

## Persistence and scope

The browser stores imported profile text, a bounded set of learned action records and completed witness receipts in **localStorage** for this site origin. This differs from the Electron version's filesystem-backed snapshots and run database. Clearing site data clears browser state. Use ledger or witness exports for independent backups.

The page uses a **bundled JSNES** core (not a CDN). It includes a basic mono NES audio path that requires a click and may depend on browser audio permissions. The page is a browser adaptation of the three-panel Gothic renderer with ternary-witness logic; it does **not** claim identical feature coverage or performance to Electron v0.4.

## Evidence/limitations

- JavaScript compilation check: bundled JSNES and application script both parsed successfully after commit.
- Github Pages deployment depends on the existing repo workflow `.github/workflows/pages.yml`. The public URL can take time to update after commit.
- Native NES gameplay and GitHub Pages browser execution have not yet been verified against an uploaded commercial ROM.

**Preserve the OASIS public root:** this app lives in `apps/the-probability/aeon/` and does not modify root `index.html`.
