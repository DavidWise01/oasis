# OaSIs Primitive Lineage v00 — 1969 → 2026-09-19

This build goes beneath the Tattoo Skill Atlas and separates:

1. **Primitive** — the smallest working concept in the model.
2. **Lineage** — selected historical changes in six-month units.
3. **Policy** — what to keep, retire/deprecate, and repair/integrate.

## Counts

- 6 domains
- 9 primitive families/domain
- 9 atoms/family
- **81 primitives/domain**
- **486 primitive atoms**
- **116 half-year timeline units** (`U000 = 1969-H1`, `U115 = 2026-H2 through 2026-09-19`)

## Domains

1. Electronics
2. Networking
3. Storage / hard-drive isolation
4. Java
5. Feng Shui / spatial heuristics
6. Art & Beauty / perception

## Forward language

```text
Alice
  ↓ encode
[ bounded BOX / channel ]
  ↓ decode
Bob
  ↓ witness / ack / error
return path
  └────────────────────→ Alice
```

The closed return path is called **toroidal** here only as an OaSIs architecture analogy.

## Historical rule

Every six-month row exists. A row with no selected lineage-breaking event says so explicitly rather than fabricating a milestone. This is a curated primitive lineage, not a claim to catalog every event in computing, design, or art history.

## Hard-drive isolation

Isolation is modeled as a ladder, not a binary checkbox:

```text
permissions
→ read-only filesystem
→ partition/volume/namespace
→ encryption + key boundary
→ device offline / driver unbound
→ controller/IOMMU/DMA boundary
→ physical data-path block
→ power removal / separate host / physical removal
→ sanitization/destruction for disposal
```

A partition is not strong isolation. Sanitization is not the same problem as runtime isolation.

## Feng Shui boundary

Feng shui is represented as a **historical/cultural spatial-design tradition**. Practical ideas such as approach, circulation, orientation, visual protection, light, clutter, and balance can be used as design heuristics. Metaphysical claims such as measurable qi are not encoded as established physical facts.

## Beauty boundary

Beauty is not reduced to one objective score. The engine keeps measurable/observable design properties — hierarchy, contrast, spacing, grouping, legibility, rhythm — separate from culture, context, and individual preference.

## Important current lineage points

- RFC 1 was published in April 1969; the first ARPANET host-to-host message followed in October 1969.
- Early monolithic TCP work evolved into separate Internet Protocol and TCP specifications.
- RFC 9293 now consolidates the modern TCP specification and obsoletes RFC 793 as the base document.
- QUIC and HTTP/3 retain application/transport primitives while changing the transport architecture.
- In 2026, IETF guidance says new TLS-based protocols must require TLS 1.3, and standards work includes hybrid post-quantum/traditional TLS key agreement.
- NIST SP 800-88 Rev.2 (2025) emphasizes a media-sanitization program and validation; runtime isolation remains a separate architectural problem.
- Java 27 is the current Java SE specification in September 2026; Java 25 is the current Oracle LTS line.
- Current UI guidance still converges on hierarchy, spacing, grouping, progressive disclosure, and accessibility.

See `source_ledger.json` for the grounding links and `timeline_1969_2026_halfyear_116.csv` for every half-year unit.