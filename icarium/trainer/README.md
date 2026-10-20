# ICARIUM Training Console · Rev 042 (One-Window Bridge)

**Live:** https://davidwise01.github.io/oasis/icarium/trainer/

Rev 042 embeds the complete Rev 040 NES arcade inside this trainer HTML file using an inherited-origin iframe `srcdoc`. The training monitor now reads the frame's `window.CONFLUENCE` API directly, including when launched as a standalone local HTML document. **No local server or second HTML file is required for the trainer bridge.**

For offline use, download `ICARIUM-TRAINING-LAB-042.zip` from the ChatGPT build artifacts, extract and double-click `ICARIUM-TRAINING-CONSOLE-042-SINGLE-FILE.html`. Load your own legally sourced .nes ROM. The cartridge and training labels are not published to GitHub.

**Tests:** headless Chromium isolated (opaque) parent origin: embedded API connected, original test NES ROM reached 264 frames with nine witnessed events and two ABCD closures at the checkpoint, control changes (risk 65%, quantum 2, fight) propagated into the emulator, observe-only and autonomous switches succeeded, zero page errors. Chrome in this test environment blocks navigating to `file://` entirely, so local disk double-click behavior on Windows has not been directly tested. Browser restart storage behavior remains unverified.

The original Rev 040 arcade remains separately available at https://davidwise01.github.io/oasis/icarium/ and is not modified by the trainer revision. No ROMs are embedded.

---
## Rev 041 baseline notes


**Live training lab:** https://davidwise01.github.io/oasis/icarium/trainer/

The trainer embeds the existing Rev 040 ICARIUM NES arcade at `../` and reads the arcade's existing `window.CONFLUENCE` observation API from the same origin. The emulation kernel is unchanged. Load a local, legally obtained NES ROM in the embedded arcade.

## What it does

- Samples current emulator frames, input masks, live adaptive policy reasoning, timing phases, screen-signature/motion diagnostics, and remembrance totals.
- Captures actual DOWN / UP / WITNESS / ABCD_CLOSURE receipts (bounded in the trainer to 5,000), with a frame-sampled plot.
- Lets you adjust the **existing** runtime risk, timing quantum and strategy controls and switch observe-only/autonomous modes.
- Offers an explicitly requested manual probe queue.
- Allows a **human** to label individual completed witnesses +1 (useful), 0 (neutral), or −1 (harmful).
- Builds a simple *shadow* recommendation ranking from those user labels using smoothed observed proportions. This is not trained image perception, and the rank is **not** silently installed as the arcade's autonomous policy.
- Imports receipts JSON (`receipts` or `agent.receipts`) as read-only training evidence, independent of emulator savestate restoration.
- Exports a bounded session JSON and a loop-profile proposal JSON with provenance and unchanged three-frame controller-neutral guardrail.

## Boundaries

No ROM, user screenshot, gameplay savestate, or private training data is committed to the Pages site. Data stays in the browser unless explicitly exported. Because the trainer uses same-origin iframe access it must be served adjacent to the arcade under the same origin; use this GitHub Pages link or the bundled ZIP via a local server rather than opening just the individual trainer HTML.

The 3-emulated-frame neutral boundary and ABCD engine are owned by Rev 040. The trainer does not bypass them for autonomous inputs.

An observed screen change is not proof of game progress. The label +1 reflects a human judgment, not a verified game-specific reward. Policy-weight and per-button action-order changes are proposal-only until explicitly implemented in a reviewed emulator revision.

## Tests

Headless Chromium 144.0 with original NES test ROM: observed API READY → ROM LIVE, hundreds of emulator frames and live witness receipts, updated risk/horizon/strategy to 60%/2 frames/fight, switched observe-only/autonomous modes, zero page errors after fixes. Shadow replay test: 3 user-labeled receipts generated a ranked loop proposal with the supported smoothed scores. Not tested with Punch-Out!! ROM or with cross-restart browser persistence.

The arcade's independent Obsidian A/B recovery remains available inside the embedded UI; it is not replaced by the training console.
