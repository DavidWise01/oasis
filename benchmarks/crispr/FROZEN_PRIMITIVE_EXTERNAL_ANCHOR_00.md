# Frozen Primitive External Immutable Anchor 00

Status: **PASS**

Canonical wrapper:
`e5050e84afbb05a6df7585dc3c0ae4f4986a5471d1b22f72a28c73da93114119`

External anchor hash:
`9c2a34b9fbe19b40cb14f8d8b8154506fb4a6219b073b2e2476a6452d2dfc9a0`

Acceptance rule:

```text
internal quorum valid
AND
external anchor matches candidate
AND
anchor epoch matches finalized tick
```

Results:

```text
canonical + intact anchor                   -> ACCEPT
3-root coordinated forgery + intact anchor -> REJECT
anchor corruption only                      -> REJECT
quorum + anchor compromised together        -> ACCEPT (new residual boundary)
stale anchor                                -> REJECT
replayed old valid anchor                   -> REJECT
dual-anchor clean                           -> ACCEPT
dual-anchor one corrupt                     -> REJECT
```

Key result:

```text
3 independent internal roots are no longer sufficient
to forge a finalized checkpoint
while the external anchor remains intact.

The remaining boundary moves outward:
internal quorum + external anchor must both be compromised.
```

RESULT = 0e
