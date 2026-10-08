# OaSIs AI Space — universe runtime v0.1

**Live page (GitHub Pages when deployed):** https://davidwise01.github.io/oasis/worlds/ai-space/

This is the first bounded **AI-universe workspace** built around the existing OaSIs architectural canon, taking the visual world layout of `worlds/u1-du0/` as a reference. U1/Du0 remains a separate speculative story world; its six evidence channels are not repurposed as proof of claims about the physical world.

## Topology

```text
ROOT0 (frozen, outside app)
    |
    +-- -+-  OBSERVE  [read/inspect/record]
    +-- +-+  CREATE   [generate/propose]
    |       (lanes cannot impersonate each other)
    +---------+-----------+
              |
       WORLD / AGENT SCOPE
              |
         HOLD PROPOSAL
              |
       INTEGRITY WITNESS
              |
        HUMAN COMMIT
              |
        APPEND-ONLY LOG
```

## Working controls

- Register external agent identities with home world, assigned lane and adapter type (manual, local, API, WASM).
- Maintain three built-in worlds: U1/Du0, Creation Studio, Research Sandbox.
- Create observation and creation tasks strictly in their assigned lanes; the browser never claims to have executed an external AI.
- Generate a SHA-256 witness over proposal identity and task fields; user must explicitly click Human commit.
- Maintain a hash-chained local event sequence with automatic verification on load and before export.
- Persist this demonstration in browser localStorage, export a JSON snapshot, reset after explicit confirmation.
- Link back to the existing U1/Du0 universe and Tattoo Studio; no existing pages are overwritten.

## Not connected / not certified

The app does **not** run arbitrary AI agents, schedule remote inference, authenticate owners, deliver secure multi-tenant isolation, synchronize across browsers, persist to Git, or implement a real RingyBoxy replicated quorum. The v34 reversible register and RingyBoxy WASM v5 are conceptual interface boundaries only in this browser prototype. A local hash proves consistency of the serialized browser event, **not** the truth of any candidate, durable authority, or tamper resistance against a malicious client. The human commit here changes **local demo state only**, never frozen canonical records.

For real external agents, implement an authenticated server adapter with capabilities, world-scoped permissions, resource limits, sandboxed execution, independently stored witness records and a human-reviewed promotion route. Avoid embedding API secrets in web pages.

## Files

- `index.html` — responsive emerald universe console
- `engine.js` — deterministic local registry/proposals/ledger logic
- `universe.json` — machine-readable world and lane schema

## Manual smoke test

1. Open page through HTTPS or localhost (browser crypto.subtle).
2. Select U1/Du0 and Archivist, type a request, click Observe.
3. Click Witness selected proposal, then Human commit.
4. Register a new creator in Research Sandbox, select it and propose creation.
5. Export ledger JSON and confirm event links and world/agent entries.
6. Attempt wrong-lane execution; it must HOLD.
7. Reset only if you want to discard the local demo history.
