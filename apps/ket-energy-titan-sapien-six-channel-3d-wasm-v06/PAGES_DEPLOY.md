# Energy Titan / Sapien six-channel 3D WASM — GitHub Pages release

**Date:** 2026-10-13  
**Source repo:** DavidWise01/oasis (public)  
**Live URL once GitHub Pages is enabled:** https://davidwise01.github.io/oasis/  
**Prepared Pages branch:** [gh-pages](https://github.com/DavidWise01/oasis/tree/gh-pages)  
**Branch commit:** `9eac5d0c43d45465dc71da2c749ed0f380e4ad97`  
**Serving file:** `gh-pages:/index.html`  
**Git blob SHA:** `e47fb4610b69f2c68de8918284b4971a4c4428da`  
**Source:** [apps/ket-energy-titan-sapien-six-channel-3d-wasm-v06/index.html](index.html)

## Published-to-branch vs live-site state

The self-contained, no-external-dependency WASM dashboard has been pushed to a dedicated `gh-pages` branch, and **the Pages branch's index.html matches the committed source Git blob exactly**. The connected GitHub integration cannot read or change the repository's GitHub Pages administration settings. Therefore **we have not confirmed the public site is live**, and do not assert successful GitHub Pages activation.

### One-time enablement action

Open [Settings → Pages](https://github.com/DavidWise01/oasis/settings/pages). Under **Build and deployment** choose:

- **Source:** Deploy from a branch
- **Branch:** gh-pages
- **Folder:** /(root)
- Click **Save**.

Then open https://davidwise01.github.io/oasis/. Initial availability is controlled by GitHub Pages deployment, not by the local simulator. Do not set the Source to GitHub Actions for this branch-based approach; this deploy contains a compiled static app and needs no Action.

## Instance proof

- Actual **WebAssembly 3D/C core** embedded directly in index.html.
- Exactly six independent logical channel nodes at `−X,+X,−Y,+Y,−Z,+Z`; origin 0 is not a seventh phone.
- Existing release: **70/70 WASM assertions** and **24/24 Chromium browser assertions** passed; no JavaScript exceptions.
- This publishing session: headless Chromium **in-memory offline page** re-instantiated; reported six nodes, 6480 cells, tick 0; Step+12 → 12; Full circuit → 372, each of six controllers at phase 372; zero JavaScript errors.
- Direct browser localhost navigation in this tool environment was blocked by administrator policy, so **no remote Pages HTTP response or hosted visual smoke test** has been confirmed.
- A prior Ansible/Nginx playbook remains a *separate* loopback-only deployment target, not necessary for GitHub Pages.

### Frozen policy

Frozen KET v2.0 stays untouched, pinned to `de8f8b80aba3a73dd371811f6b4be39df92e45ce`. The six radio/energy paths are simulated packet-routing and cellular activity only, not a physical wireless energy transfer implementation.

## Updating later

For a new additive WASM release, update the source under a *new versioned* app path. Once verified, create a new Pages branch commit with the new self-contained index.html and preserve this deployment record for provenance.
