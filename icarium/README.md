# ICARIUM / CONFLUENCE · Rev 040 Remembrance

**Live arcade:** https://davidwise01.github.io/oasis/icarium/

This directory publishes the standalone Rev 040 offline-compatible NES emulator / autonomous experimental agent dashboard from the ongoing SAPPHON / ICARIUM project.

## Run

1. Open the live arcade URL in a modern desktop browser.
2. Select a local, legally obtained **.nes** cartridge file in the Emulator Controls panel.
3. Choose autonomous, manual, deterministic, or observe-only mode.
4. Use the remembrance, evidence, temporal, ABCD timing, and Obsidian modules to inspect observations and controller receipts.
5. Export saved snapshots/receipts if you need to retain evidence outside browser storage.

No game ROMs are provided or embedded. All emulator JavaScript is bundled inside `index.html`; no external API key or backend service is required.

## Controls and interpretation

- NES inputs are A, B, SELECT, START, UP, DOWN, LEFT and RIGHT.
- The ABCD reciprocal timing controller maintains a 3-emulated-frame zero-input boundary between actions.
- An observed screen signature change is **not proof of successful game progress**.
- Temporal “future” values are hypotheses from recorded transitions, not guaranteed outcomes.
- The 3D diagnostics are symbolic, not claims of physical entanglement.
- Remembrance keeps bounded observed state → action → witnessed state episodes.
- Obsidian A/B recovery and browser persistence depend on browser storage permissions; export snapshots as separate backups. Private ROMs and emulator snapshots should not be committed to this public Pages directory.

## Release evidence

Rev 040 was headless-tested before publication using an original small test NES ROM: 721 emulated frames, 27 controller presses and releases, 26 remembrance episodes, six ABCD closures, and zero reported JavaScript exceptions. Punch-Out!! gameplay success and true cross-restart browser persistence have **not** been independently verified.

Published as an additive subdirectory on the existing `gh-pages` branch; the main OASIS site is unchanged.
