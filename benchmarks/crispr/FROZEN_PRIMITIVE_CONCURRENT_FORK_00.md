# Frozen Primitive Concurrent Fork 00

Status: **PASS**

Race condition:
- two valid children
- same parent
- same sequence number
- same tick
- both individually valid

Deterministic rule:
`winner = min(child_hashes)`

Winner:
`7806a9448ef3ef1b7d74acfd44d19bb7986905df7fea76f7c0cf45438fad66d3`

Loser:
`7e0627f43a3685d27f1d6b17ba5e37d29c66d17dc033601e9914ff1e2de43a6b`

Checks:
- input order independence
- exactly one canonical child
- losing descendants rejected from canonical lineage
- winning descendant accepted
- replay does not change winner
- late arrival does not change winner
- quorum counts only canonical-branch witnesses

```text
parent
  |
  +---- child B ----> descendant B
  |
  +---- child C ----> descendant C

same tick / same seq

deterministic hash tie-break
        |
        v
one canonical branch
one rejected fork

RESULT = 0e
```
