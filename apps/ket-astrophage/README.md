# Confluence / Ssaphone Substrate — Cross-Discipline Stack v3.0

**Target:** `DavidWise01/oasis/apps/ket-astrophage/` (GitHub Pages).  
**Expected URL:** <https://davidwise01.github.io/oasis/apps/ket-astrophage/#analogy>  
**Date:** 2026-10-14. **Model status:** additive interface / frozen KET kernel unchanged.

## Canonical four-band threshold grammar

| Gate | Exact fraction | Synthetic integer ticks of 300 | Typical function |
|---|---:|---:|---|
| `1/4w` | 1/4 | 75 | detect |
| `2/3m` | 2/3 | 200 | couple / integrate |
| `3/4s` | 3/4 | 225 | act / transition |
| `4/4-+` | 4/4 | 300 | verify, reconcile, close |

The slider is **integer-valued 0–300**, so all four fractions are exact rather than approximately rounded floating-point comparisons. Its value is a normalized control-simulation parameter; it is *not* a measurement of physical strength, biological age, electromagnetic energy, nuclear forces, likelihood, reliability or performance.

- `0..74` = standby; `75..199` = weak; `200..224` = medium; `225..299` = strong.
- At 300 ticks, closure is *requested* but still **blocked** unless the user supplies a separate simulated witness flag. The checkbox is only a user-controlled teaching prop—not real cryptographic proof or authorization.
- The same 18 discipline mappings are simultaneously visible as a scrollable crosswalk and individually selectable. Groups: computing & control (6), life sciences (4), physical systems (3), human / cultural systems (5).

## How to use

Open the static page, scroll to **Disciplines**, select a mapping, drag the slider or use the exact four presets, and optionally add a simulated witness at the final gate. Prior sections—Protocol, Substrate, Astrophage Field, Cycle, Encoder, and Evidence—remain present.

## Classification

- **A** — direct procedural software mapping can be implemented with explicit thresholds and checkable receipts (not universal measured constants).
- **B** — a scientific or engineering mechanism exists, but Confluence's particular threshold assignments are illustrative.
- **C** — a philosophical, educational, aesthetic, or societal analogy; no numerical correspondence is claimed.

The **per-domain caveat** is part of the canonical mapping. All sources are available as clickable references in the page and in `analogy-stack-v1.json`. A source corroborates the underlying domain-specific mechanism where appropriate, **not** the universal correctness of these four percentages.

A key biological limit: electrical membrane potentials do influence patterning, but there is no established universal four-threshold law for life or epigenetic inheritance. Gestational F0, F1, and F2 may be directly exposed; evidence of transmission to an unexposed F3 is a separate research question. Neural action potentials are all-or-none rather than graded in amplitude by this model. `-+` is a receipt/return operator, not energy creation.

## Verification and preservation

```sh
node apps/ket-astrophage/test_page.cjs
```

The test suite verifies the original 44-register round trips and Genesis safeguards, plus manifest consistency, domain completeness, exact rational tick gates, and witness requirement. Browser interaction checks at 1440 px and 390 px widths also exercise the slider, presets, selection, witness, original cycle/codec, and quarantine drill. No external code or stylesheet is necessary to open `index.html` offline.

- `index.html` — interactive standalone GitHub page (fully embedded discipline dataset).
- `analogy-stack-v1.json` — machine-readable independent source of 18 discipline mappings.
- `test_page.cjs` — Node.js regression and threshold tests.
- The frozen `architecture/astrophage-full-stack-v1/`, `architecture/character-register-44/`, `kernel/`, and original root homepage are **not edited**.
- Genesis is intentionally TERMINATED / DISABLED; all interfaces are standalone simulations. This release does not conduct research on people, manipulate cell signaling, or track real-world events.

## Select underlying references

- Bioelectric patterning: <https://pubmed.ncbi.nlm.nih.gov/33999994/>
- Epigenetic inheritance limitations: <https://www.nature.com/articles/s41467-018-05445-5>
- Neural action potentials: <https://openstax.org/books/anatomy-and-physiology-2e/pages/12-4-the-action-potential>
- ECN networking: <https://www.rfc-editor.org/rfc/rfc3168>
- NIST CSF 2.0 has **six functions**, not Confluence's four gates: <https://www.nist.gov/news-events/news/2024/02/nist-releases-version-20-landmark-cybersecurity-framework>