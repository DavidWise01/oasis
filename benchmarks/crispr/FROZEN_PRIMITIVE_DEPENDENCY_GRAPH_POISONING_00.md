# Frozen Primitive Dependency Graph Poisoning 00

Status: **PASS**

Canonical wrapper:
`f25e14fb07112891fcd16529ba9c52d4e164d1e3f5adcf90001a6fc6700aa02b`

Attack:
EXT1 lies about its DNS ancestry so that the claimed graph appears independent from EXT0.

Results:

```text
poisoned self-report appears independent     -> YES
independent observer finds shared DNS root   -> DETECT
claimed/observed closure discrepancy         -> DETECT
claimed 3 domains / observed 2 domains       -> DETECT
graph disagreement                           -> FAIL CLOSED
dependency omission                          -> DETECT
invented dependency                          -> DETECT
two independent observers agree              -> CONFIRM
```

Key rule:

```text
anchor self-reported graph
!= trusted dependency truth

effective quorum must use
independently observed / corroborated dependency closures
```

Observed correlation:

```text
EXT0 -> DNS_A -> DNS_ROOT_X
EXT1 -> DNS_B -> DNS_ROOT_X

EXT1 claims:
DNS_B -> DNS_ROOT_FAKE

observer catches:
omitted  DNS_ROOT_X
invented DNS_ROOT_FAKE
```

RESULT = 0e
