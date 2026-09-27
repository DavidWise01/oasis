# Frozen Primitive Anchor Administration Independence 00

Status: **PASS**

Canonical wrapper:
`f25e14fb07112891fcd16529ba9c52d4e164d1e3f5adcf90001a6fc6700aa02b`

Anchor independence now requires separation across:
- signing key
- operator
- storage backend
- publication path

Results:

```text
2 fully independent anchors             -> ACCEPT
shared signing key                      -> REJECT
shared operator                         -> REJECT
shared storage backend                  -> REJECT
shared publication path                 -> REJECT
different IDs / same admin domain       -> REJECT
3 anchor IDs / 2 real domains           -> COUNT AS 2
3 anchor IDs / 3 real domains           -> COUNT AS 3
```

Key invariant:

```text
anchor_id != failure domain

independent anchor =
independent signer
AND independent operator
AND independent storage
AND independent publication path
```

RESULT = 0e
