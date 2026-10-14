# Confluence v3 — alignment and test receipt

**Audit date:** 2026-10-14 (America/Chicago).
**Scope:** The additive Confluence GitHub Pages interface, 44-symbol register, six-phase regenerative loop, Astrophage typed adapter, and 18-domain four-band analogy dataset.
**Repository:** `DavidWise01/oasis`. Prior Confluence v3 content commit: `0a7830d518e7c58e8bd65cf88abe6f78607ade47`.
**Frozen KET core:** No changes requested or made by this alignment.

## Structural contract

| Stage | Exact address | Expected behavior |
|---|---:|---|
| Standby | 0–74 / 300 | no threshold reached |
| 1/4w | 75–199 / 300 | detect |
| 2/3m | 200–224 / 300 | couple |
| 3/4s | 225–299 / 300 | activate |
| 4/4-+ | 300 / 300 | require independently supplied *simulated* witness for closure |

- The domain crosswalk has exactly 18 mappings in four domain families, each with a caveat.
- The witness checkbox is a teaching simulation, not a cryptographic signature or authentication.
- Genesis remains **TERMINATED / DISABLED**; fail-drill faults are quarantined without overwriting an earlier witness.
- `n` is address 0 in the 44-symbol registry; `.0x` is one token. The UTF-8 bridge converts each byte to **two base-44 addresses**.
- OSIMODEL bus: 8 lanes × 208 logical slots per lane = 1,664 *logical* addresses; address reuse is allowed and packet ordinals preserve order.
- The six-phase `LIVE → WRITE → REMEMBER → FORGET → READ → LIVE` routine shares the returning LIVE event and records SHA-256 receipts.
- Threshold fractions are *model parameters*. This report does not assert universal biological, electromagnetic, nuclear, or epigenetic laws.

## Executed tests

| Suite | Local result |
|---|---:|
| 44-symbol registry | 114/114 |
| Six-phase regenerative cycle | 39/39 |
| Typed Astrophage adapter | 303/303 |
| Confluence v3 combined mapping + UI invariants | 688/688 |
| **Aggregate** | **1,144/1,144** |

The tests above were run locally against the preserved v3 and frozen-stack source archives. The archives do not claim byte-for-byte identity with every live repository file. The committed CI workflow executes directly from GitHub checkout to independently validate the repository head.

### Independent headless browser checks

Using Chromium with the packaged v3 HTML at **1440×900** and **390×900**:

- **0 uncaught JavaScript errors** and **no horizontal overflow** at either width.
- All **18 discipline mappings** render and can be selected.
- All **four exact gate buttons** set the correct 300-tick position.
- At 300 ticks, missing witness displays **BLOCKED: MISSING WITNESS**.
- Toggling the simulated witness permits **SIMULATED RECEIPT VERIFIED**; unchecking blocks again.
- Fault injection quarantines the invalid state; reset returns to READY.
- Existing UTF-8 encoder and cycle controls remain responsive.
- `window.CONFLUENCE_V3_AUDIT` reports 18 domains, 4 groups, exact gates, blocked unwitnessed closure, and disabled Genesis.

Browser smoke tests are **manual/local**; GitHub Actions workflow added here executes the four Node test suites, not Chromium. Publishing on GitHub Pages is managed by the repository's pre-existing `.github/workflows/pages.yml`. GitHub Pages live deployment and production-security certification are **not asserted**.

## Reproduction

```sh
node architecture/character-register-44/test_register.mjs
node architecture/regenerative-loop/ket-cycle-v01/test_cycle.mjs
node architecture/astrophage-full-stack-v1/test_adapter.mjs
node apps/ket-astrophage/test_page.cjs
```

An additive workflow at `.github/workflows/confluence-stack-regression.yml` re-runs these on PRs, relevant pushes, and manual dispatch. No test mutates KET frozen architecture.
