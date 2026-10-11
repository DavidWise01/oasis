# KELVIN v11.3 — Measured Execution / Performance Report

**Measured:** 2026-10-11 UTC  
**Original kernel commit:** `b3c92a0816f491d75bf91f2f437e439fbd054f5f`  
**Result:** **13/13 Node checks PASS, 9/9 Chromium DOM checks PASS**.  
**Benchmark/report only:** Frozen parent and deployed application source unchanged.

## Source provenance

Local copies of both files matched their exact committed Git blob identities using `git hash-object`:

| Source file | Git blob SHA |
|---|---|
| `projects/sapphon-li/kelvin.mjs` | `e1b239e96f5e6eb39cac795e0eb6d8bb73c74e7d` |
| `projects/sapphon-li/kelvin.html` | `418bee292fd084ff0fb80e2396c6176a2675ab0d` |

Runtime: **Node.js v22.16.0**, Linux x64 container on AMD EPYC 9V74 (virtualized scheduling). Browser: **Chromium 144.0.7559.96**.

## Functional execution

13 Node-side checks passed:
- Existing invariants: one parent tensor, one shared 3D field, two signed faces, i/u/us tracks.
- First shell: `-++- S` / +LILLITH; first manual advancement: `+--+ N` / -EVE; 720° return: `-++- S` / +LILLITH.
- No unsolicited state change; two explicit ledger entries after two steps.
- Immutable outward state and no external corruption of internal ledger via copied export.
- Alternation correct across all 128 manual steps, with exact closed limit: step 129 raises `RangeError` and does not advance.
- Reports and compact JSON ledger serialize at turn 128.
- Benchmark execution completed.

9 Chromium DOM checks passed:
- Page structure + kernel logic initializes and renders.
- First click flips to EVE and second click returns to LILLITH.
- 100 synchronous click events increment the turn to 102.
- After 128 total steps, advance button is disabled.
- Export button downloads JSON containing exactly 128 steps; no browser page exceptions.
- At 390-pixel mobile viewport, no horizontal document overflow and manual advance works.

### Important browser-host caveat

This container's Chromium blocks navigation to `http://127.0.0.1` and `file://` with `net::ERR_BLOCKED_BY_ADMINISTRATOR`. To exercise the actual UI event-handling logic in a browser, the HTML was injected via `page.set_content`, with the committed JS module body injected in-page and its import/export **loader directives** removed. Thus the tests validate the real DOM and JS functional logic but **do not verify standard ES module loading, deployment, live website navigation, or real-user latency**.

## Performance — local Node hot path

**Medians** of 7 trials (128-step and ledger use 5 trials); warmed JavaScript VM. Times are local point measurements, not guaranteed hardware-independent rates.

| Operation | Operations per trial | Median latency | Throughput |
|---|---:|---:|---:|
| Kernel instantiation + read | 50,000 | 134.6 ns | 7,429,565/s |
| `current()` | 200,000 | 49.9 ns | 20,044,234/s |
| `report()` | 15,000 | 258.3 ns | 3,872,099/s |
| Entire **128-step** cycle | 1,500 | 20,746.3 ns = 0.02075 ms | 48,201 cycles/s |
| `ledger()` at 128-step cap | 4,000 | 21,386.4 ns = 0.02139 ms | 46,759/s |

Compact Node JSON export at cap: 39,068 bytes.

## Chromium in-page DOM benchmark

In 100 consecutive synchronous button-triggered transitions including state update and DOM render:
- **mean 0.055 ms/event**, p95 **0.200 ms/event**;
- median rounded to **0.000 ms**, which only means **below timer resolution**, not zero work;
- in-page script injection initialisation **81.516 ms**, including Playwright evaluation, **not** equivalent to a cold network page load;
- browser pretty JSON export: 53,688 bytes.

Desktop screenshot captured at 1280×900. Mobile screenshot captured at 390×844.

## Scope

Tests establish behavior and computational cost of the **symbolic finite-state kernel** only. They do **not** establish a physical spin-1/2 implementation, gravitational or gravity waves, cosmological history, measurable Earth expansion, or a physical shadow world.

Frozen source and KELVIN v11.3 runtime were **not modified**. Original manual-only / terminal Gen-1 SAPPHON boundaries remain intact.
