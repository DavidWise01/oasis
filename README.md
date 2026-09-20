# OaSIs

**OaSIs is an open, append-only engine for building domain tools from explicit primitives.**

The public repo now starts with **Feng Shui / spatial design** as the first domain lens, then descends through the primitive stack and out into attachments such as Tattoo.

## Public map

```text
O^1 immutable parent
│
├─ domains/
│  └─ feng-shui/          81 spatial primitives
│
├─ knowledge/
│  ├─ primitives/         electronics → networking → storage → Java → space → art
│  └─ tattoo/             tattoo skill atlas
│
├─ architecture/
│  └─ box-toroid.md       Alice → channel → Bob → witness/return
│
├─ apps/
│  └─ tattoo/             current creative attachment
│
├─ lean/                  formal modules and stitch ledger
└─ legacy/                preserved prior public root material
```

## Core communication primitive

```text
Alice
  ↓ encode
[ bounded BOX / channel ]
  ↓ decode
Bob
  ↓
witness / ACK / error / provenance
  └────────────────────────→ Alice
```

"Toroidal" in this repository is an OaSIs architectural analogy for the closed return / verification path. It is not a claim that the Internet or physical space is literally a torus.

## Attachment rule

Every attachment gets a fresh domain engine.

The internals may be very deep. The human surface should stay small and understandable. Recommendations may be offered; the person makes the final creative decision.

## Evidence discipline

OaSIs distinguishes:

- software invariants from claims about the external world;
- cultural or symbolic models from experimentally established physical claims;
- provenance from legal adjudication;
- deterministic output from truth.

## GitHub Pages

The root `index.html` is the public site. A Pages deployment workflow lives at `.github/workflows/pages.yml`.

Expected project-page URL:

`https://davidwise01.github.io/oasis/`

## Historical preservation

The previous root page and README are preserved under `legacy/`; they are not treated as the current project description.
