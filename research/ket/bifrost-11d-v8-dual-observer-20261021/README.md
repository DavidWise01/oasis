# BIFROST V8 — dual observer boundary

Canonical literal: `[bifrost(d<| -+5{0}S+- |>d)]`.

V7 is preserved. Two symmetric `d` observers independently propose the next receipt core. A receipt is accepted only if the two observers agree on the same hash, parent hash, sequence, endpoints, and amount. Duplicate proposals for an already recorded digest have no additional effect; conflicting proposals are rejected and quarantined. The central token `-+5{0}S+-` is preserved verbatim; **S has no assigned semantics**.

14 adjacent edges across 122–125, 140–145 and 360–366. All balances begin with 100 units; transfer is 2.5% of current source, with equal credit. Source reference rose / `0vwxyz`; 24 channels and 60 phase bins belong to the inherited V7 geometry.

Run `python bifrost_v8.py`. Tests exercise observer agreement, core hash integrity, 14 receipts, global conservation, distinct chain digests, duplicate proposals, altered amount rejection, and chain parent continuity. These are simulated observers, **not** independently hosted network nodes and not a Byzantine fault tolerant quorum. No SQL.
