# P3.69 — Durable anchor prototype and external checkpoint boundary

Date: 2026-10-09. Retains the user-specified outer topology `-+5 + 1` with five signed lanes and one independently trusted anchor. Adds a Node.js filesystem-backed reservation ledger keyed by witness and epoch and SHA-256 transcript checkpoint. Does not change four prime photon identities, six signed directional axes or 64^-n nesting.

**Executed locally:** Node 22, 13 assertions PASS: initial reservation, restart with retained checkpoint, same-vote replay, double-vote rejection, new epoch, deleted record detection, corrupt record detection, missing directory fail-close. Source and test committed to main.

**Limits:** The checkpoint is supplied to the process by a hypothetical external trusted authority; the code does not create such an authority. The prototype's mutable in-memory `trusted` field is not automatically durable. It does not ensure concurrency serializability of multiple different-epoch writes, power-loss atomicity, safe initialization after lost trust state, or resistance to simultaneous rollback of both checkpoint and files. `provision()` is meant for explicitly authorized genesis only and must not be called during automatic recovery. Not production-ready.

Next target P3.70: transactional durable watermark backed by separately audited, authenticated witness records and race testing under concurrent epochs.
