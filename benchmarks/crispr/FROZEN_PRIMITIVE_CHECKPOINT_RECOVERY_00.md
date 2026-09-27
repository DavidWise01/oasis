# Frozen Primitive Checkpoint Recovery 00

Status: **PASS**

Quorum: **3-of-5**

Canonical checkpoint wrapper hash:
`efb5d0aecb31dc50552e3cac6d1ff8021946b64bf5471024f2b5564b2724f9ce`

Tests:

```text
clean control                  -> PASS
stored seq corruption          -> RECOVER EXACT
stored hash corruption         -> RECOVER EXACT
1 forged witness               -> REJECT FORGERY / RECOVER EXACT
2 colluding forged witnesses   -> REJECT FORGERY / RECOVER EXACT
3 colluding forged witnesses   -> FALSE RECOVERY becomes possible
local loss + 2 forged          -> RECOVER EXACT
exact serialization recovery   -> PASS

RESULT = 0e
```

Important threshold:

```text
3-of-5 recovery
tolerates <= 2 coordinated forged witness copies

3 matching forged copies
can reconstruct the wrong checkpoint

Therefore recovery quorum inherits the same independence/provenance requirement as validation quorum.
```
