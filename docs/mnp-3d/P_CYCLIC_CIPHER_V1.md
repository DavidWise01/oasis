# TESSY :: Cyclic P Cipher v1

**Exact author notation (preserved):**

```text
{{ -p{{ast reads}+}present{+{lives{+{future{+{writes} }}}}}}}
```

This is the temporal **p** cipher, deliberately separate from the provenance `-d / -d+ / +d` operators.

| Phase | Action | Invariant |
|---|---|---|
| `-p` | Past reads | Inspect existing witnessed/committed events; do not invent history |
| `-p+` | Present lives | Record current event/decision inside BOXY |
| `+p` | Future writes | Stage an output or prediction; it is not yet a verified outcome |
| TURN | Advance the cycle | Append the written output as a prior **record** for the next tick, not as proof it came true |

```text
PAST READ → PRESENT LIVE → FUTURE WRITE → TURN → PAST READ → …
```

The pinned `0@[v,w,x,y,z]`, axes `x=state, y=space, z=time/what happened`, and QUANTA `OBSERVE → ESTIMATE → PREDICT → WITNESS → UPDATE` stay unchanged. Written predictions enter past as **predictions that were written**, not truths; NOM's independent timestamp ledger remains read-only. The locked foundation/candidate grammar remains independent.

No physical quantum claim. Implementation `p-cycle-v1.js`; regression test `test-p-cycle-v1.cjs`.
