# Frozen Primitive Anchor Split-Brain 00

Status: **PASS**

Canonical wrapper:
`f25e14fb07112891fcd16529ba9c52d4e164d1e3f5adcf90001a6fc6700aa02b`

Alternate wrapper:
`314f13efb6ce39cfa216ea93f3b6d42f2ed608f0916a0c1478f05551f8d81518`

Results:

```text
dual anchors agree                  -> ACCEPT
same epoch / different wrappers     -> REJECT
same wrapper / conflicting epochs   -> REJECT
delayed second anchor               -> REJECT until published
delayed anchor later agrees         -> ACCEPT
stale anchor replay                 -> REJECT
all required anchors jointly forged -> ACCEPT (residual boundary)
3-anchor 2-of-3 majority            -> ACCEPT canonical 2/3
```

Fail-closed rule:

```text
required anchors must be available
AND
agree on wrapper
AND
agree on epoch
```

Residual boundary:

```text
if all required external anchors are jointly compromised
and publish the same forged wrapper + epoch,
the anchor layer cannot distinguish the forgery internally.
```

RESULT = 0e
