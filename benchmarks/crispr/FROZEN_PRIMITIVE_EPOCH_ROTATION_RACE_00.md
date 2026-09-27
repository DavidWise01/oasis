# Frozen Primitive Epoch Rotation Race 00

Status: **PASS**

Parent epoch:
`49368a25911d9945e5bdb1f99a6f2abeab313730aade7ac08814efe94d14752e`

Candidate successors:
- A: `72c63adbae0c16ece5298d9bb358897218ad18c6259d877775333d6d2153c515`
- B: `a15dd3689cb1ccf26a2aafac258a786e56cb77d5b30f71980a3e681b07705c57`

Canonical winner:
`72c63adbae0c16ece5298d9bb358897218ad18c6259d877775333d6d2153c515`

Loser:
`a15dd3689cb1ccf26a2aafac258a786e56cb77d5b30f71980a3e681b07705c57`

Deterministic rule:
`winner = min(valid_successor_hashes)`

Results:

```text
arrival order reversal              -> SAME WINNER
candidate replay                    -> SAME WINNER
one canonical rotation              -> PASS
winner continuation                 -> PASS
loser continuation                  -> REJECT
late loser after finality           -> NO REWRITE
tie-break reproducibility           -> PASS
next observer/key binding           -> PASS
loser fork evidence retained        -> PASS

RESULT = 0e
```

Core invariant:

```text
one parent epoch
      |
      +-- successor A
      |
      +-- successor B

deterministic resolver
      |
      v
one canonical rotation

once finalized:
losing key lineage may be retained as evidence,
but it cannot become canonical later.
```
