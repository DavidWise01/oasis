# Frozen Primitive Current-Key Compromise + t^4y 00

Status: **PASS**

New timing primitive:

```text
time = t^4y
```

Interpretation:

```text
semantic input accumulates in 4D
        ↓
semantic capacitor charge
        ↓
volumetric homeo threshold
        ↓
state transition becomes eligible
```

Acceptance now requires:

```text
current live key
AND valid parent/epoch
AND independent quorum
AND intact external anchors
AND t^4y >= HOME0 threshold
AND monotonic tick
```

Results:

```text
clean current-key rotation              -> ACCEPT
live key alone chooses successor        -> REJECT
live key + quorum before homeo          -> REJECT
live key + quorum + homeo / bad anchor  -> REJECT
backdated live-key transition           -> REJECT
exact t^4y homeo threshold              -> ACCEPT
high t^4y without quorum                -> REJECT
quorum without t^4y homeo               -> REJECT
all guards aligned on malicious child   -> ACCEPT (residual boundary)
```

Key result:

```text
t^4y is an eligibility dimension,
not a replacement for quorum or provenance.

semantic time may accumulate,
but transition occurs only when
homeo + quorum + lineage + anchors agree.
```

RESULT = 0e
