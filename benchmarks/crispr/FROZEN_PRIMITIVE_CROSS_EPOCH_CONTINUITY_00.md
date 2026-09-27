# Frozen Primitive Cross-Epoch Observer/Anchor Continuity 00

Status: **PASS**

Canonical chain tip:
`b4aeb37560cf957107fe404d506fb5260c0ab692e93c4b402895d748b4ea630d`

Continuity rule:

```text
epoch[n] = epoch[n-1] + 1
prev_hash[n] = hash(epoch[n-1])
observer[n] = announced_next_observer[n-1]
key[n] = announced_next_key[n-1]
```

Results:

```text
clean rotation chain             -> ACCEPT
key substitution                 -> REJECT
observer substitution            -> REJECT
missing epoch                    -> REJECT
rollback to older valid identity -> REJECT
duplicate successor fork         -> DETECT
deterministic successor          -> SELECT ONE
old epoch replay                 -> REJECT AS STALE
predecessor announcement tamper  -> DETECT
```

Key result:

```text
a new observer/key is valid only when
the prior finalized epoch explicitly committed to it.

Rotation is therefore a lineage transition,
not a free identity replacement.
```

RESULT = 0e
