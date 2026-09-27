# Frozen Primitive Post-Rotation Key Compromise 00

Status: **PASS**

Canonical tip:
`2f248a41cd7cf61bbc81619f233e9dbf1ec6d46fd066cbe3382911df76dbb7ed`

Rule:

```text
child.observer == parent.next_observer
child.key      == parent.next_key
child.prev     == parent.hash
child.epoch    == parent.epoch + 1
child.tick     >  parent.tick
```

Results:

```text
current authorized key extends chain     -> ACCEPT
retired K1 extends current tip           -> REJECT
old K2 masquerades as current observer   -> REJECT
retired branch resurrection              -> REJECT
backdated replacement                    -> REJECT
finalized rotation record rewrite        -> DETECT
old structurally valid child             -> REJECT AS STALE
old finalized epoch replay               -> REJECT AS STALE
canonical tip after attacks              -> UNCHANGED
```

Key result:

```text
compromise of a retired key
does not restore its former authority.

authority is lineage-scoped and forward-only.
```

RESULT = 0e
